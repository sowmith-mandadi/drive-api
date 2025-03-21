import { Component, OnInit, OnDestroy, HostListener } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { Subscription } from 'rxjs';
import { debounceTime, distinctUntilChanged, switchMap, finalize } from 'rxjs/operators';
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

/**
 * Search component for finding and filtering conference content
 * Includes both traditional and AI-powered search capabilities
 */
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
  
  // Pagination variables
  totalPages: number = 0;
  displayedPages: number[] = [];
  paginationRange: number = 5; // Number of page buttons to show
  
  // Advanced filters toggle
  showAdvancedFilters: boolean = false;
  
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
  
  // Search history
  searchHistory: string[] = [];
  
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
    this.loadSearchHistory();
    
    // Subscribe to query param changes
    this.subs.add(
      this.route.queryParams.subscribe(params => {
        // Handle page parameter
        if (params['page']) {
          this.currentPage = parseInt(params['page'], 10);
        }
        
        // Handle page size parameter
        if (params['pageSize']) {
          this.pageSize = parseInt(params['pageSize'], 10);
        }
        
        if (params['query']) {
          this.searchForm.get('query')?.setValue(params['query'], { emitEvent: false });
          this.search();
          this.addToSearchHistory(params['query']);
        } else {
          this.loadRecentContent();
        }
        
        // Handle AI search toggle
        if (params['ai'] === 'true') {
          this.searchForm.get('useAi')?.setValue(true, { emitEvent: false });
          this.isAiSearch = true;
        }
      })
    );
    
    // Subscribe to search input changes
    this.subs.add(
      this.searchForm.get('query')!.valueChanges
        .pipe(
          debounceTime(350), // Reduced from 500ms for more responsive feel
          distinctUntilChanged()
        )
        .subscribe(query => {
          if (query && query.length > 2) {
            this.updateQueryParam(query);
          } else if (query === '') {
            // Clear search and load recent content
            this.updateQueryParam('');
            this.loadRecentContent();
          }
        })
    );
    
    // Subscribe to AI search toggle changes
    this.subs.add(
      this.searchForm.get('useAi')!.valueChanges.subscribe(useAi => {
        this.isAiSearch = useAi;
        this.router.navigate([], {
          relativeTo: this.route,
          queryParams: { ai: useAi },
          queryParamsHandling: 'merge'
        });
        
        if (this.searchForm.get('query')?.value) {
          this.search();
        }
      })
    );
  }
  
  /**
   * Clean up subscriptions on component destruction
   */
  ngOnDestroy(): void {
    this.subs.unsubscribe();
  }
  
  /**
   * Handle keyboard shortcuts for search navigation
   * @param event Keyboard event
   */
  @HostListener('window:keydown', ['$event'])
  handleKeyboardEvent(event: KeyboardEvent): void {
    // Only handle if not in input or textarea
    if (document.activeElement instanceof HTMLInputElement || 
        document.activeElement instanceof HTMLTextAreaElement) {
      return;
    }
    
    // Navigate to next/previous page with arrow keys
    if (event.altKey && event.key === 'ArrowRight') {
      this.goToNextPage();
      event.preventDefault();
    } else if (event.altKey && event.key === 'ArrowLeft') {
      this.goToPreviousPage();
      event.preventDefault();
    }
    
    // Focus search box with / key
    if (event.key === '/' && !(document.activeElement instanceof HTMLInputElement)) {
      const searchInput = document.querySelector('input[formControlName="query"]') as HTMLInputElement;
      if (searchInput) {
        searchInput.focus();
        event.preventDefault();
      }
    }
  }
  
  /**
   * Initialize the search form
   */
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
  
  /**
   * Load recent search history from local storage
   */
  loadSearchHistory(): void {
    const history = localStorage.getItem('searchHistory');
    if (history) {
      this.searchHistory = JSON.parse(history);
    }
  }
  
  /**
   * Add search term to history
   * @param term Search term to add
   */
  addToSearchHistory(term: string): void {
    if (!term || term.trim() === '' || this.searchHistory.includes(term)) {
      return;
    }
    
    // Add to beginning of array and keep only last 10 searches
    this.searchHistory.unshift(term);
    if (this.searchHistory.length > 10) {
      this.searchHistory = this.searchHistory.slice(0, 10);
    }
    
    localStorage.setItem('searchHistory', JSON.stringify(this.searchHistory));
  }
  
  /**
   * Clear search history
   */
  clearSearchHistory(): void {
    this.searchHistory = [];
    localStorage.removeItem('searchHistory');
  }
  
  /**
   * Load recent content when no search query is present
   */
  loadRecentContent(): void {
    this.loading = true;
    this.contentService.getRecentContent(this.currentPage, this.pageSize)
      .pipe(
        finalize(() => this.loading = false)
      )
      .subscribe(
        response => {
          this.searchResults = response.content;
          this.totalResults = response.totalCount;
          this.updatePagination();
        },
        error => {
          console.error('Error loading recent content:', error);
          this.snackBar.open('Error loading content. Please try again.', 'Close', {
            duration: 3000
          });
        }
      );
  }
  
  /**
   * Perform search based on current parameters
   */
  search(): void {
    const query = this.searchForm.get('query')?.value;
    const useAi = this.searchForm.get('useAi')?.value;
    
    if (!query) {
      this.loadRecentContent();
      return;
    }
    
    this.loading = true;
    this.isAiSearch = useAi;
    
    // Combine all filters into one object
    const filters = {
      tracks: this.selectedTracks,
      tags: this.selectedTags,
      sessionDates: this.selectedSessionDates,
      sessionTypes: this.selectedSessionTypes,
      learningLevels: this.selectedLearningLevels,
      topics: this.selectedTopics,
      jobRoles: this.selectedJobRoles,
      areasOfInterest: this.selectedAreasOfInterest,
      industries: this.selectedIndustries
    };
    
    if (useAi) {
      // Use RAG for AI-powered search
      this.searchWithRAG(query, filters);
    } else {
      // Use traditional search
      this.searchTraditional(query, filters);
    }
  }
  
  /**
   * Perform AI-powered search using RAG
   * @param query Search query
   * @param filters Applied filters
   */
  searchWithRAG(query: string, filters: any): void {
    this.ragService.askQuestion(query, undefined, filters)
      .pipe(
        finalize(() => this.loading = false)
      )
      .subscribe(
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
                this.updatePagination();
              },
              error => {
                console.error('Error fetching content details:', error);
                this.snackBar.open('Error fetching content details. Please try again.', 'Close', {
                  duration: 3000
                });
              }
            );
          } else {
            this.searchResults = [];
            this.totalResults = 0;
            this.updatePagination();
          }
        },
        error => {
          console.error('Error performing AI search:', error);
          this.snackBar.open('Error performing AI search. Please try again or use traditional search.', 'Close', {
            duration: 3000
          });
        }
      );
  }
  
  /**
   * Perform traditional search
   * @param query Search query
   * @param filters Applied filters
   */
  searchTraditional(query: string, filters: any): void {
    this.contentService.searchContent(query, filters, this.currentPage, this.pageSize)
      .pipe(
        finalize(() => this.loading = false)
      )
      .subscribe(
        response => {
          this.searchResults = response.content;
          this.totalResults = response.totalCount;
          this.updatePagination();
        },
        error => {
          console.error('Error searching content:', error);
          this.snackBar.open('Error searching content. Please try again.', 'Close', {
            duration: 3000
          });
        }
      );
  }
  
  /**
   * Update query parameter in URL
   * @param query Search query
   */
  updateQueryParam(query: string): void {
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { 
        query,
        page: this.currentPage,
        pageSize: this.pageSize
      },
      queryParamsHandling: 'merge'
    });
  }
  
  /**
   * Update pagination variables based on search results
   */
  updatePagination(): void {
    this.totalPages = Math.ceil(this.totalResults / this.pageSize);
    this.updateDisplayedPages();
  }
  
  /**
   * Update the array of page numbers displayed in pagination
   */
  updateDisplayedPages(): void {
    this.displayedPages = [];
    
    if (this.totalPages <= this.paginationRange) {
      // Show all pages if less than paginationRange
      for (let i = 1; i <= this.totalPages; i++) {
        this.displayedPages.push(i);
      }
    } else {
      // Calculate start and end page numbers
      let startPage = Math.max(1, this.currentPage - Math.floor(this.paginationRange / 2));
      let endPage = startPage + this.paginationRange - 1;
      
      // Adjust if endPage exceeds total
      if (endPage > this.totalPages) {
        endPage = this.totalPages;
        startPage = Math.max(1, endPage - this.paginationRange + 1);
      }
      
      // Add first page and ellipsis if needed
      if (startPage > 1) {
        this.displayedPages.push(1);
        if (startPage > 2) {
          this.displayedPages.push(-1); // -1 represents ellipsis
        }
      }
      
      // Add page numbers
      for (let i = startPage; i <= endPage; i++) {
        this.displayedPages.push(i);
      }
      
      // Add last page and ellipsis if needed
      if (endPage < this.totalPages) {
        if (endPage < this.totalPages - 1) {
          this.displayedPages.push(-1); // -1 represents ellipsis
        }
        this.displayedPages.push(this.totalPages);
      }
    }
  }
  
  /**
   * Handle page change from custom pagination or paginator
   * @param event Page change event
   */
  onPageChange(event: any): void {
    let pageIndex: number;
    
    if (event instanceof PageEvent) {
      // From Material paginator
      pageIndex = event.pageIndex + 1;
      this.pageSize = event.pageSize;
    } else {
      // From custom pagination
      pageIndex = event;
    }
    
    if (pageIndex !== this.currentPage) {
      this.currentPage = pageIndex;
      this.updateQueryParam(this.searchForm.get('query')?.value || '');
      this.search();
      
      // Scroll to top of results
      setTimeout(() => {
        const resultsElement = document.querySelector('.results-panel');
        if (resultsElement) {
          resultsElement.scrollIntoView({ behavior: 'smooth' });
        }
      }, 100);
    }
  }
  
  /**
   * Navigate to specific page
   * @param page Page number
   */
  goToPage(page: number): void {
    if (page !== -1 && page !== this.currentPage) {
      this.onPageChange(page);
    }
  }
  
  /**
   * Navigate to next page
   */
  goToNextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.onPageChange(this.currentPage + 1);
    }
  }
  
  /**
   * Navigate to previous page
   */
  goToPreviousPage(): void {
    if (this.currentPage > 1) {
      this.onPageChange(this.currentPage - 1);
    }
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
  
  /**
   * Highlight search terms in text
   * @param text Text to highlight
   * @returns HTML with highlighted terms
   */
  highlightSearchTerms(text: string): string {
    if (!text) return '';
    
    const searchTerm = this.searchForm.get('query')?.value;
    if (!searchTerm) return text;
    
    // Escape special characters in the search term
    const escapedSearchTerm = searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    
    // Create a regex to find all instances of the search term (case insensitive)
    const regex = new RegExp(`(${escapedSearchTerm})`, 'gi');
    
    // Replace all instances with highlighted version
    return text.replace(regex, '<span class="search-highlight">$1</span>');
  }
  
  /**
   * Toggle advanced filters visibility
   */
  toggleAdvancedFilters(): void {
    this.showAdvancedFilters = !this.showAdvancedFilters;
  }
  
  /**
   * Apply the selected filters
   */
  applyFilters(): void {
    this.currentPage = 1;
    this.search();
    this.showAdvancedFilters = false;
  }
  
  /**
   * Check if any filters are active
   * @returns True if at least one filter is selected
   */
  hasActiveFilters(): boolean {
    return this.selectedTracks.length > 0 || 
           this.selectedTags.length > 0 || 
           this.selectedSessionDates.length > 0 || 
           this.selectedSessionTypes.length > 0 || 
           this.selectedLearningLevels.length > 0 || 
           this.selectedTopics.length > 0 || 
           this.selectedJobRoles.length > 0 || 
           this.selectedAreasOfInterest.length > 0 || 
           this.selectedIndustries.length > 0;
  }
  
  /**
   * Get the total count of active filters
   * @returns Number of active filters
   */
  getActiveFilterCount(): number {
    return this.selectedTracks.length + 
           this.selectedTags.length + 
           this.selectedSessionDates.length + 
           this.selectedSessionTypes.length + 
           this.selectedLearningLevels.length + 
           this.selectedTopics.length + 
           this.selectedJobRoles.length + 
           this.selectedAreasOfInterest.length + 
           this.selectedIndustries.length;
  }
  
  /**
   * Get a list of all active filters for display
   * @returns Array of filter objects with type, id and label
   */
  getActiveFiltersList(): Array<{type: string, id: string, label: string}> {
    const filters: Array<{type: string, id: string, label: string}> = [];
    
    // Add tracks
    this.selectedTracks.forEach(trackId => {
      const track = this.getTrackById(trackId);
      if (track) {
        filters.push({
          type: 'track',
          id: trackId,
          label: `Track: ${track.name}`
        });
      }
    });
    
    // Add tags
    this.selectedTags.forEach(tag => {
      filters.push({
        type: 'tag',
        id: tag,
        label: `Tag: ${tag}`
      });
    });
    
    // Add session dates
    this.selectedSessionDates.forEach(dateId => {
      const date = this.getSessionDateById(dateId);
      if (date) {
        filters.push({
          type: 'sessionDate',
          id: dateId,
          label: `Date: ${date.date}`
        });
      }
    });
    
    // Add session types
    this.selectedSessionTypes.forEach(typeId => {
      const type = this.getSessionTypeById(typeId);
      if (type) {
        filters.push({
          type: 'sessionType',
          id: typeId,
          label: `Type: ${type.name}`
        });
      }
    });
    
    // Add learning levels
    this.selectedLearningLevels.forEach(levelId => {
      const level = this.getLearningLevelById(levelId);
      if (level) {
        filters.push({
          type: 'learningLevel',
          id: levelId,
          label: `Level: ${level.name}`
        });
      }
    });
    
    // Add topics
    this.selectedTopics.forEach(topicId => {
      const topic = this.getTopicById(topicId);
      if (topic) {
        filters.push({
          type: 'topic',
          id: topicId,
          label: `Topic: ${topic.name}`
        });
      }
    });
    
    // Add job roles
    this.selectedJobRoles.forEach(roleId => {
      const role = this.getJobRoleById(roleId);
      if (role) {
        filters.push({
          type: 'jobRole',
          id: roleId,
          label: `Role: ${role.name}`
        });
      }
    });
    
    // Add areas of interest
    this.selectedAreasOfInterest.forEach(areaId => {
      const area = this.getAreaOfInterestById(areaId);
      if (area) {
        filters.push({
          type: 'areaOfInterest',
          id: areaId,
          label: `Interest: ${area.name}`
        });
      }
    });
    
    // Add industries
    this.selectedIndustries.forEach(industryId => {
      const industry = this.getIndustryById(industryId);
      if (industry) {
        filters.push({
          type: 'industry',
          id: industryId,
          label: `Industry: ${industry.name}`
        });
      }
    });
    
    return filters;
  }
  
  /**
   * Remove a filter by its type and id
   * @param filter Filter object to remove
   */
  removeFilter(filter: {type: string, id: string, label: string}): void {
    switch (filter.type) {
      case 'track':
        this.selectedTracks = this.selectedTracks.filter(id => id !== filter.id);
        break;
      case 'tag':
        this.selectedTags = this.selectedTags.filter(tag => tag !== filter.id);
        break;
      case 'sessionDate':
        this.selectedSessionDates = this.selectedSessionDates.filter(id => id !== filter.id);
        break;
      case 'sessionType':
        this.selectedSessionTypes = this.selectedSessionTypes.filter(id => id !== filter.id);
        break;
      case 'learningLevel':
        this.selectedLearningLevels = this.selectedLearningLevels.filter(id => id !== filter.id);
        break;
      case 'topic':
        this.selectedTopics = this.selectedTopics.filter(id => id !== filter.id);
        break;
      case 'jobRole':
        this.selectedJobRoles = this.selectedJobRoles.filter(id => id !== filter.id);
        break;
      case 'areaOfInterest':
        this.selectedAreasOfInterest = this.selectedAreasOfInterest.filter(id => id !== filter.id);
        break;
      case 'industry':
        this.selectedIndustries = this.selectedIndustries.filter(id => id !== filter.id);
        break;
    }
    
    this.currentPage = 1;
    this.search();
  }
} 