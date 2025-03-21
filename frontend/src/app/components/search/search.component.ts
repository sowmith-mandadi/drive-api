import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { debounceTime, distinctUntilChanged, switchMap } from 'rxjs/operators';
import { ContentService } from '../../services/content.service';
import { RagService } from '../../services/rag.service';
import { ConferenceDataService } from '../../services/conference-data.service';
import { Content, RagResponse, Track } from '../../models/content.model';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Observable, of } from 'rxjs';

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.scss']
})
export class SearchComponent implements OnInit {
  searchForm!: FormGroup;
  searchResults: Content[] = [];
  totalResults: number = 0;
  currentPage: number = 1;
  pageSize: number = 10;
  loading: boolean = false;
  
  // For filters
  tracks: Track[] = [];
  selectedTracks: string[] = [];
  availableTags: string[] = [];
  selectedTags: string[] = [];
  
  // For AI-powered search
  isAiSearch: boolean = false;
  ragResponse: RagResponse | null = null;
  
  constructor(
    private fb: FormBuilder,
    private contentService: ContentService,
    private ragService: RagService,
    private conferenceDataService: ConferenceDataService,
    private route: ActivatedRoute,
    private router: Router,
    private snackBar: MatSnackBar
  ) { }
  
  ngOnInit(): void {
    this.createForm();
    this.loadFilters();
    
    // Subscribe to query param changes
    this.route.queryParams.subscribe(params => {
      if (params['query']) {
        this.searchForm.get('query')?.setValue(params['query']);
        this.search();
      } else {
        this.loadRecentContent();
      }
    });
    
    // Subscribe to search input changes
    this.searchForm.get('query')?.valueChanges
      .pipe(
        debounceTime(500),
        distinctUntilChanged(),
        switchMap(query => {
          if (query && query.length > 2) {
            return of(query);
          }
          return of(null);
        })
      )
      .subscribe(query => {
        if (query) {
          this.updateQueryParam(query);
        }
      });
  }
  
  createForm(): void {
    this.searchForm = this.fb.group({
      query: [''],
      useAi: [true]
    });
  }
  
  loadFilters(): void {
    // Load tracks for filters
    this.conferenceDataService.getTracks().subscribe(
      tracks => {
        this.tracks = tracks;
      },
      error => {
        console.error('Error loading tracks:', error);
      }
    );
    
    // Load popular tags
    this.contentService.getPopularTags().subscribe(
      tags => {
        this.availableTags = tags;
      },
      error => {
        console.error('Error loading tags:', error);
      }
    );
  }
  
  loadRecentContent(): void {
    this.loading = true;
    this.contentService.getRecentContent(this.currentPage, this.pageSize).subscribe(
      response => {
        this.searchResults = response.content;
        this.totalResults = response.totalCount;
        this.loading = false;
      },
      error => {
        console.error('Error loading recent content:', error);
        this.loading = false;
        this.snackBar.open('Error loading content. Please try again.', 'Close', {
          duration: 3000
        });
      }
    );
  }
  
  search(): void {
    const query = this.searchForm.get('query')?.value;
    const useAi = this.searchForm.get('useAi')?.value;
    
    if (!query) {
      this.loadRecentContent();
      return;
    }
    
    this.loading = true;
    this.isAiSearch = useAi;
    
    if (useAi) {
      // Use RAG for AI-powered search
      this.searchWithRAG(query);
    } else {
      // Use traditional search
      this.searchTraditional(query);
    }
  }
  
  searchWithRAG(query: string): void {
    const filters = {
      tracks: this.selectedTracks,
      tags: this.selectedTags
    };
    
    this.ragService.askQuestion(query, undefined, filters).subscribe(
      response => {
        this.ragResponse = response;
        
        // Get content IDs from passages
        const contentIds = response.passages
          .map(passage => passage.source)
          .filter((value, index, self) => self.indexOf(value) === index); // Remove duplicates
        
        // Get full content details for the IDs
        if (contentIds.length > 0) {
          this.contentService.getContentByIds(contentIds).subscribe(
            contents => {
              this.searchResults = contents;
              this.totalResults = contents.length;
              this.loading = false;
            },
            error => {
              console.error('Error fetching content details:', error);
              this.loading = false;
              this.snackBar.open('Error fetching content details. Please try again.', 'Close', {
                duration: 3000
              });
            }
          );
        } else {
          this.searchResults = [];
          this.totalResults = 0;
          this.loading = false;
        }
      },
      error => {
        console.error('Error performing AI search:', error);
        this.loading = false;
        this.snackBar.open('Error performing AI search. Please try again or use traditional search.', 'Close', {
          duration: 3000
        });
      }
    );
  }
  
  searchTraditional(query: string): void {
    const filters = {
      tracks: this.selectedTracks,
      tags: this.selectedTags
    };
    
    this.contentService.searchContent(query, filters, this.currentPage, this.pageSize).subscribe(
      response => {
        this.searchResults = response.content;
        this.totalResults = response.totalCount;
        this.loading = false;
      },
      error => {
        console.error('Error searching content:', error);
        this.loading = false;
        this.snackBar.open('Error searching content. Please try again.', 'Close', {
          duration: 3000
        });
      }
    );
  }
  
  updateQueryParam(query: string): void {
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { query },
      queryParamsHandling: 'merge'
    });
  }
  
  // Toggle track filter
  toggleTrack(trackId: string): void {
    const index = this.selectedTracks.indexOf(trackId);
    if (index === -1) {
      this.selectedTracks.push(trackId);
    } else {
      this.selectedTracks.splice(index, 1);
    }
    this.search();
  }
  
  // Toggle tag filter
  toggleTag(tag: string): void {
    const index = this.selectedTags.indexOf(tag);
    if (index === -1) {
      this.selectedTags.push(tag);
    } else {
      this.selectedTags.splice(index, 1);
    }
    this.search();
  }
  
  clearFilters(): void {
    this.selectedTracks = [];
    this.selectedTags = [];
    this.search();
  }
  
  onPageChange(event: any): void {
    this.currentPage = event.pageIndex + 1;
    this.pageSize = event.pageSize;
    this.search();
  }
  
  getTrackById(trackId: string): Track | undefined {
    return this.tracks.find(track => track.id === trackId);
  }
  
  findSimilarDocuments(contentId: string): void {
    this.loading = true;
    this.ragService.findSimilarDocuments(undefined, contentId).subscribe(
      similarDocs => {
        this.searchResults = similarDocs;
        this.totalResults = similarDocs.length;
        this.loading = false;
        this.searchForm.get('query')?.setValue('');
        this.updateQueryParam('');
        this.snackBar.open('Showing similar documents', 'Close', {
          duration: 3000
        });
      },
      error => {
        console.error('Error finding similar documents:', error);
        this.loading = false;
        this.snackBar.open('Error finding similar documents. Please try again.', 'Close', {
          duration: 3000
        });
      }
    );
  }
} 