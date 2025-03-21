import { Component, OnInit, OnDestroy } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { debounceTime, distinctUntilChanged, switchMap } from 'rxjs/operators';
import { ContentService } from '../../services/content.service';
import { RagService } from '../../services/rag.service';
import { ConferenceDataService } from '../../services/conference-data.service';
import { 
  Content, 
  RagResponse, 
  Track, 
  SessionType, 
  SessionDate, 
  LearningLevel, 
  Topic, 
  JobRole, 
  AreaOfInterest, 
  Industry 
} from '../../models/content.model';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Observable, of } from 'rxjs';
import { PageEvent } from '@angular/material/paginator';

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.scss']
})
export class SearchComponent implements OnInit, OnDestroy {
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
  
  // New filters
  sessionDates: SessionDate[] = [];
  selectedSessionDates: string[] = [];
  
  sessionTypes: SessionType[] = [];
  selectedSessionTypes: string[] = [];
  
  learningLevels: LearningLevel[] = [];
  selectedLearningLevels: string[] = [];
  
  topics: Topic[] = [];
  selectedTopics: string[] = [];
  
  jobRoles: JobRole[] = [];
  selectedJobRoles: string[] = [];
  
  areasOfInterest: AreaOfInterest[] = [];
  selectedAreasOfInterest: string[] = [];
  
  industries: Industry[] = [];
  selectedIndustries: string[] = [];
  
  // For AI-powered search
  isAiSearch: boolean = false;
  ragResponse: RagResponse | null = null;
  
  private subs = new Subscription();
  
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
    
    // Subscribe to AI search toggle changes
    this.subs.add(
      this.searchForm.get('useAi')!.valueChanges.subscribe(useAi => {
        this.isAiSearch = useAi;
        if (this.searchForm.get('query')?.value) {
          this.search();
        }
      })
    );
    
    // Auto-search on query changes (with debounce)
    this.subs.add(
      this.searchForm.get('query')!.valueChanges
        .pipe(
          debounceTime(500),
          distinctUntilChanged()
        )
        .subscribe(() => {
          if (this.searchForm.get('query')?.value?.length > 2 || 
              !this.searchForm.get('query')?.value) {
            this.currentPage = 1;
            this.search();
          }
        })
    );
  }
  
  ngOnDestroy(): void {
    this.subs.unsubscribe();
  }
  
  createForm(): void {
    this.searchForm = this.fb.group({
      query: [''],
      useAi: [false]
    });
  }
  
  loadFilters(): void {
    // Initialize session dates
    this.sessionDates = [
      { id: 'april-9', date: 'April 9' },
      { id: 'april-10', date: 'April 10' },
      { id: 'april-11', date: 'April 11' }
    ];
    
    // Initialize session types
    this.sessionTypes = [
      { id: 'keynotes', name: 'Keynotes' },
      { id: 'spotlights', name: 'Spotlights' },
      { id: 'breakouts', name: 'Breakouts' },
      { id: 'cloud-talks', name: 'Cloud talks' },
      { id: 'developer-meetups', name: 'Developer Meetups' },
      { id: 'expo-experiences', name: 'Expo Experiences' },
      { id: 'learning-center-workshops', name: 'Learning Center Workshops' },
      { id: 'lightning-talks', name: 'Lightning Talks' },
      { id: 'lounge-sessions', name: 'Lounge Sessions' },
      { id: 'showcase-demos', name: 'Showcase Demos' },
      { id: 'solution-talks', name: 'Solution Talks' }
    ];
    
    // Initialize learning levels
    this.learningLevels = [
      { id: 'introductory', name: 'Introductory' },
      { id: 'technical', name: 'Technical' },
      { id: 'advanced-technical', name: 'Advanced Technical' },
      { id: 'general', name: 'General' }
    ];
    
    // Initialize topics
    this.topics = [
      { id: 'apis', name: 'APIs' },
      { id: 'app-dev', name: 'App Dev' },
      { id: 'applied-ai', name: 'Applied AI' },
      { id: 'architecture', name: 'Architecture' },
      { id: 'business-intelligence', name: 'Business Intelligence' },
      { id: 'chrome', name: 'Chrome' },
      { id: 'compute', name: 'Compute' },
      { id: 'cost-optimization', name: 'Cost Optimization' },
      { id: 'data-analytics', name: 'Data Analytics' },
      { id: 'databases', name: 'Databases' },
      { id: 'firebase', name: 'Firebase' },
      { id: 'gender', name: 'Gender' },
      { id: 'kaggle', name: 'Kaggle' },
      { id: 'migration', name: 'Migration' },
      { id: 'multicloud', name: 'Multicloud' },
      { id: 'networking', name: 'Networking' },
      { id: 'security', name: 'Security' },
      { id: 'serverless', name: 'Serverless' },
      { id: 'storage', name: 'Storage' },
      { id: 'vertex-ai', name: 'Vertex AI' },
      { id: 'workspace', name: 'Workspace' }
    ];
    
    // Initialize job roles
    this.jobRoles = [
      { id: 'application-developers', name: 'Application Developers' },
      { id: 'data-professionals', name: 'Data Analysts, Data Scientists, Data Engineers' },
      { id: 'database-professionals', name: 'Database Professionals' },
      { id: 'devops', name: 'DevOps, IT Ops, Platform Engineers, SREs' },
      { id: 'executive', name: 'Executive' },
      { id: 'infrastructure', name: 'Infrastructure Architects & Operators' },
      { id: 'it-managers', name: 'IT Managers & Business Technology Leaders' },
      { id: 'security-professionals', name: 'Security Professionals' }
    ];
    
    // Initialize areas of interest
    this.areasOfInterest = [
      { id: 'build-for-everyone', name: 'Build for Everyone' },
      { id: 'customer-story', name: 'Customer Story' },
      { id: 'developer-experiences', name: 'Developer Experiences' },
      { id: 'partner-innovation', name: 'Partner Innovation' },
      { id: 'small-it-teams', name: 'Small IT Teams' },
      { id: 'startup', name: 'Startup' },
      { id: 'sustainability', name: 'Sustainability' },
      { id: 'technology-leadership', name: 'Technology & Leadership' }
    ];
    
    // Initialize industries
    this.industries = [
      { id: 'consumer-packaged-goods', name: 'Consumer & Packaged Goods' },
      { id: 'cross-industry-solutions', name: 'Cross-Industry Solutions' },
      { id: 'education', name: 'Education' },
      { id: 'financial-services', name: 'Financial Services' },
      { id: 'games', name: 'Games' },
      { id: 'government', name: 'Government' },
      { id: 'healthcare-life-sciences', name: 'Healthcare & Life Sciences' },
      { id: 'manufacturing', name: 'Manufacturing' },
      { id: 'media-entertainment', name: 'Media & Entertainment' },
      { id: 'public-sector', name: 'Public Sector' },
      { id: 'retail', name: 'Retail' },
      { id: 'supply-chain-logistics', name: 'Supply Chain & Logistics' },
      { id: 'technology', name: 'Technology' },
      { id: 'telecommunications', name: 'Telecommunications' }
    ];
    
    // Load tracks for filters
    this.subs.add(
      this.conferenceDataService.getTracks().subscribe(
        tracks => {
          this.tracks = tracks;
        },
        error => {
          console.error('Error loading tracks:', error);
        }
      )
    );
    
    // Load popular tags
    this.subs.add(
      this.contentService.getPopularTags().subscribe(
        tags => {
          this.availableTags = tags;
        },
        error => {
          console.error('Error loading tags:', error);
          // Fallback to sample tags
          this.availableTags = [
            'Angular', 'React', 'Vue', 'Svelte', 'JavaScript',
            'TypeScript', 'GraphQL', 'REST', 'API', 'Cloud',
            'DevOps', 'Docker', 'Kubernetes', 'AI', 'ML',
            'Python', 'Java', 'Frontend', 'Backend', 'Fullstack'
          ];
        }
      )
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
  
  // Add toggle methods for new filters
  toggleSessionDate(dateId: string): void {
    const index = this.selectedSessionDates.indexOf(dateId);
    if (index === -1) {
      this.selectedSessionDates.push(dateId);
    } else {
      this.selectedSessionDates.splice(index, 1);
    }
    this.currentPage = 1;
    this.search();
  }
  
  toggleSessionType(typeId: string): void {
    const index = this.selectedSessionTypes.indexOf(typeId);
    if (index === -1) {
      this.selectedSessionTypes.push(typeId);
    } else {
      this.selectedSessionTypes.splice(index, 1);
    }
    this.currentPage = 1;
    this.search();
  }
  
  toggleLearningLevel(levelId: string): void {
    const index = this.selectedLearningLevels.indexOf(levelId);
    if (index === -1) {
      this.selectedLearningLevels.push(levelId);
    } else {
      this.selectedLearningLevels.splice(index, 1);
    }
    this.currentPage = 1;
    this.search();
  }
  
  toggleTopic(topicId: string): void {
    const index = this.selectedTopics.indexOf(topicId);
    if (index === -1) {
      this.selectedTopics.push(topicId);
    } else {
      this.selectedTopics.splice(index, 1);
    }
    this.currentPage = 1;
    this.search();
  }
  
  toggleJobRole(roleId: string): void {
    const index = this.selectedJobRoles.indexOf(roleId);
    if (index === -1) {
      this.selectedJobRoles.push(roleId);
    } else {
      this.selectedJobRoles.splice(index, 1);
    }
    this.currentPage = 1;
    this.search();
  }
  
  toggleAreaOfInterest(areaId: string): void {
    const index = this.selectedAreasOfInterest.indexOf(areaId);
    if (index === -1) {
      this.selectedAreasOfInterest.push(areaId);
    } else {
      this.selectedAreasOfInterest.splice(index, 1);
    }
    this.currentPage = 1;
    this.search();
  }
  
  toggleIndustry(industryId: string): void {
    const index = this.selectedIndustries.indexOf(industryId);
    if (index === -1) {
      this.selectedIndustries.push(industryId);
    } else {
      this.selectedIndustries.splice(index, 1);
    }
    this.currentPage = 1;
    this.search();
  }
  
  clearFilters(): void {
    this.selectedTracks = [];
    this.selectedTags = [];
    this.selectedSessionDates = [];
    this.selectedSessionTypes = [];
    this.selectedLearningLevels = [];
    this.selectedTopics = [];
    this.selectedJobRoles = [];
    this.selectedAreasOfInterest = [];
    this.selectedIndustries = [];
    this.currentPage = 1;
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
  
  // Helper methods for getting names
  getSessionDateById(dateId: string): SessionDate | undefined {
    return this.sessionDates.find(date => date.id === dateId);
  }
  
  getSessionTypeById(typeId: string): SessionType | undefined {
    return this.sessionTypes.find(type => type.id === typeId);
  }
  
  getLearningLevelById(levelId: string): LearningLevel | undefined {
    return this.learningLevels.find(level => level.id === levelId);
  }
  
  getTopicById(topicId: string): Topic | undefined {
    return this.topics.find(topic => topic.id === topicId);
  }
  
  getJobRoleById(roleId: string): JobRole | undefined {
    return this.jobRoles.find(role => role.id === roleId);
  }
  
  getAreaOfInterestById(areaId: string): AreaOfInterest | undefined {
    return this.areasOfInterest.find(area => area.id === areaId);
  }
  
  getIndustryById(industryId: string): Industry | undefined {
    return this.industries.find(industry => industry.id === industryId);
  }
} 