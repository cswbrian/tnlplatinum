import React, { useState, useEffect, useMemo, useCallback } from 'react';
import './App.css';
import headerImage from './assets/header-min.png';
import youtubeIcon from './assets/youtube.svg';
import songsData from './data/songs.json';
import adsData from './data/ads.json';
import supportingActorsData from './data/supporting-actors.json';
import varietyShowsData from './data/variety-shows.json';
import auditionFilmsData from './data/audition-films.json';
import filmsData from './data/films.json';

// Lazy loading hook for large datasets
const useLazyData = (data: any[], chunkSize: number = 50) => {
  const [loadedCount, setLoadedCount] = useState(chunkSize);
  
  const loadMore = useCallback(() => {
    setLoadedCount(prev => Math.min(prev + chunkSize, data.length));
  }, [data.length, chunkSize]);
  
  const loadedData = useMemo(() => {
    return data.slice(0, loadedCount);
  }, [data, loadedCount]);
  
  const hasMore = loadedCount < data.length;
  
  return { loadedData, hasMore, loadMore, totalCount: data.length };
};

// Debounce hook for search optimization
const useDebounce = (value: string, delay: number) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

// Virtual scrolling hook
const useVirtualScroll = (items: any[], itemHeight: number, containerHeight: number) => {
  const [scrollTop, setScrollTop] = useState(0);
  
  const visibleItemCount = Math.ceil(containerHeight / itemHeight);
  const startIndex = Math.floor(scrollTop / itemHeight);
  const endIndex = Math.min(startIndex + visibleItemCount + 2, items.length); // +2 for buffer
  
  const visibleItems = items.slice(startIndex, endIndex);
  const totalHeight = items.length * itemHeight;
  const offsetY = startIndex * itemHeight;
  
  return {
    visibleItems,
    totalHeight,
    offsetY,
    setScrollTop
  };
};

const App: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState<string>('films');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [watchedItems, setWatchedItems] = useState<Record<string, Set<string>>>({
    films: new Set(),
    songs: new Set(),
    ads: new Set(),
    'audition-films': new Set(),
    'variety-shows': new Set(),
    'supporting-actors': new Set()
  });

  // Debounce search term to improve performance
  const debouncedSearchTerm = useDebounce(searchTerm, 300);

  // Helper function to highlight searched text
  const highlightText = useCallback((text: string, searchTerm: string) => {
    if (!searchTerm.trim()) return text;
    
    const regex = new RegExp(`(${searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, index) => 
      regex.test(part) ? (
        <mark key={index} className="highlighted-text">{part}</mark>
      ) : (
        part
      )
    );
  }, []);

  // Load watched items from localStorage on component mount
  useEffect(() => {
    const savedWatchedItems = localStorage.getItem('tnlplatinum-watched-items');
    if (savedWatchedItems) {
      try {
        const parsed = JSON.parse(savedWatchedItems);
        const converted: Record<string, Set<string>> = {};
        Object.keys(parsed).forEach(category => {
          converted[category] = new Set(parsed[category]);
        });
        setWatchedItems(converted);
      } catch (error) {
        console.error('Error loading watched items from localStorage:', error);
      }
    }
  }, []);

  // Save watched items to localStorage whenever they change
  useEffect(() => {
    const serialized: Record<string, string[]> = {};
    Object.keys(watchedItems).forEach(category => {
      serialized[category] = Array.from(watchedItems[category]);
    });
    localStorage.setItem('tnlplatinum-watched-items', JSON.stringify(serialized));
  }, [watchedItems]);

  // Handle YouTube search
  const handleYouTubeSearch = useCallback((fullTitle: string) => {
    const encodedQuery = encodeURIComponent(fullTitle);
    const youtubeUrl = `https://www.youtube.com/results?search_query=${encodedQuery}`;
    window.open(youtubeUrl, '_blank', 'noopener,noreferrer');
  }, []);

  const toggleWatched = useCallback((itemId: string, category: string) => {
    setWatchedItems(prev => {
      const newWatchedItems = { ...prev };
      const categorySet = new Set(newWatchedItems[category]);
      
      if (categorySet.has(itemId)) {
        categorySet.delete(itemId);
      } else {
        categorySet.add(itemId);
      }
      
      newWatchedItems[category] = categorySet;
      return newWatchedItems;
    });
  }, []);

  const categories = [
    { id: 'films', name: '最佳電影', data: filmsData, count: filmsData.length },
    { id: 'songs', name: '最佳原創電影歌曲', data: songsData, count: songsData.length },
    { id: 'ads', name: '最佳廣告片', data: adsData, count: adsData.length },
    { id: 'audition-films', name: '最佳試音片', data: auditionFilmsData, count: auditionFilmsData.length },
    { id: 'variety-shows', name: '最佳綜藝', data: varietyShowsData, count: varietyShowsData.length },
    { id: 'supporting-actors', name: '最佳搭膊頭', data: supportingActorsData, count: supportingActorsData.length },
  ];

  const currentCategory = categories.find(cat => cat.id === selectedCategory);
  
  // Memoize filtered data to prevent unnecessary re-computations
  const filteredData = useMemo(() => {
    if (!currentCategory) return [];
    
    return currentCategory.data.filter((item: any) => {
      if (selectedCategory === 'supporting-actors') {
        return item.toLowerCase().includes(debouncedSearchTerm.toLowerCase());
      }
      
      if (selectedCategory === 'films') {
        const searchFields = [
          item.title,
          item.fullTitle,
          item.director,
          item.writer,
          item.leadActor,
          item.leadActress,
          item.supportingActor,
          item.supportingActress,
          item.newActor,
          item.editor,
          item.cinematographer,
          item.actionDesign,
          item.artDirector,
          item.visualEffects,
          item.month
        ].filter(Boolean);
        return searchFields.some(field => 
          field.toLowerCase().includes(debouncedSearchTerm.toLowerCase())
        );
      }
      
      const searchFields = [
        item.title || item.song || item.name,
        item.fullTitle,
        item.movie,
        item.director
      ].filter(Boolean);
      return searchFields.some(field => 
        field.toLowerCase().includes(debouncedSearchTerm.toLowerCase())
      );
    });
  }, [currentCategory, selectedCategory, debouncedSearchTerm]);

  // Handle loading state for search
  useEffect(() => {
    if (selectedCategory === 'films' && debouncedSearchTerm !== searchTerm) {
      setIsLoading(true);
      const timer = setTimeout(() => setIsLoading(false), 100);
      return () => clearTimeout(timer);
    }
  }, [selectedCategory, debouncedSearchTerm, searchTerm]);

  // Lazy loading for films data
  const { loadedData: lazyFilteredFilms, hasMore, loadMore } = useLazyData(
    selectedCategory === 'films' ? filteredData : [],
    100 // Load 100 items at a time
  );

  // Virtual scrolling for films
  const filmsContainerRef = React.useRef<HTMLDivElement>(null);
  const [filmsContainerHeight, setFilmsContainerHeight] = useState(600);
  const FILM_CARD_HEIGHT = 200; // Approximate height of film card

  const {
    visibleItems: visibleFilms,
    totalHeight: filmsTotalHeight,
    offsetY: filmsOffsetY,
    setScrollTop: setFilmsScrollTop
  } = useVirtualScroll(
    selectedCategory === 'films' ? lazyFilteredFilms : [],
    FILM_CARD_HEIGHT,
    filmsContainerHeight
  );

  // Update container height on mount and resize
  useEffect(() => {
    const updateHeight = () => {
      if (filmsContainerRef.current) {
        const rect = filmsContainerRef.current.getBoundingClientRect();
        setFilmsContainerHeight(window.innerHeight - rect.top); // 100px buffer
      }
    };

    updateHeight();
    window.addEventListener('resize', updateHeight);
    return () => window.removeEventListener('resize', updateHeight);
  }, []);

  const handleFilmsScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
    setFilmsScrollTop(scrollTop);
    
    // Load more data when user scrolls near the bottom
    if (hasMore && scrollTop + clientHeight >= scrollHeight - 200) {
      loadMore();
    }
  }, [setFilmsScrollTop, hasMore, loadMore]);

  const renderFilmCard = useCallback((item: any) => {
    const filmId = `${item.title}-${item.director || ''}`;
    const isWatched = watchedItems.films.has(filmId);
    
    return (
      <div key={`${item.title}-${item.director || ''}`} className="nominee-card film-card">
        <div className="nominee-title">
          <div className="nominee-title-text">{highlightText(item.title, debouncedSearchTerm)}</div>
          <div className="watched-checkbox" onClick={() => toggleWatched(filmId, 'films')}>
            <span className={`checkbox ${isWatched ? 'checked' : ''}`}>
              {isWatched ? '✓' : ''}
            </span>
            <span className="watched-text">睇過</span>
          </div>
        </div>
        {item.fullTitle && item.fullTitle !== item.title && (
          <div className="nominee-subtitle" onClick={() => handleYouTubeSearch(item.fullTitle)}>
            <img src={youtubeIcon} alt="YouTube" className="youtube-icon" />
            {highlightText(item.fullTitle, debouncedSearchTerm)}
          </div>
        )}
        <div className="film-meta">
          {item.director && (
            <div className="film-detail">
              <span className="detail-label">導演：</span>
              <span className="detail-value">{highlightText(item.director, debouncedSearchTerm)}</span>
            </div>
          )}
          {item.writer && (
            <div className="film-detail">
              <span className="detail-label">編劇：</span>
              <span className="detail-value">{highlightText(item.writer, debouncedSearchTerm)}</span>
            </div>
          )}
          {item.leadActor && (
            <div className="film-detail">
              <span className="detail-label">男主角：</span>
              <span className="detail-value">{highlightText(item.leadActor, debouncedSearchTerm)}</span>
            </div>
          )}
          {item.leadActress && (
            <div className="film-detail">
              <span className="detail-label">女主角：</span>
              <span className="detail-value">{highlightText(item.leadActress, debouncedSearchTerm)}</span>
            </div>
          )}
          {item.supportingActor && (
            <div className="film-detail">
              <span className="detail-label">男配角：</span>
              <span className="detail-value">{highlightText(item.supportingActor, debouncedSearchTerm)}</span>
            </div>
          )}
          {item.supportingActress && (
            <div className="film-detail">
              <span className="detail-label">女配角：</span>
              <span className="detail-value">{highlightText(item.supportingActress, debouncedSearchTerm)}</span>
            </div>
          )}
          {item.newActor && (
            <div className="film-detail">
              <span className="detail-label">新演員：</span>
              <span className="detail-value">{highlightText(item.newActor, debouncedSearchTerm)}</span>
            </div>
          )}
          {item.editor && (
            <div className="film-detail">
              <span className="detail-label">剪接：</span>
              <span className="detail-value">{highlightText(item.editor, debouncedSearchTerm)}</span>
            </div>
          )}
          {item.cinematographer && (
            <div className="film-detail">
              <span className="detail-label">攝影：</span>
              <span className="detail-value">{highlightText(item.cinematographer, debouncedSearchTerm)}</span>
            </div>
          )}
          {item.actionDesign && (
            <div className="film-detail">
              <span className="detail-label">動作設計：</span>
              <span className="detail-value">{highlightText(item.actionDesign, debouncedSearchTerm)}</span>
            </div>
          )}
          {item.artDirector && (
            <div className="film-detail">
              <span className="detail-label">美術指導：</span>
              <span className="detail-value">{highlightText(item.artDirector, debouncedSearchTerm)}</span>
            </div>
          )}
          {item.visualEffects && (
            <div className="film-detail">
              <span className="detail-label">視覺效果：</span>
              <span className="detail-value">{highlightText(item.visualEffects, debouncedSearchTerm)}</span>
            </div>
          )}
        </div>
        <div className="nominee-date">{item.releaseDate}</div>
      </div>
    );
  }, [highlightText, debouncedSearchTerm, watchedItems.films, toggleWatched, handleYouTubeSearch]);

  const renderNomineeCard = useCallback((item: any, index: number) => {
    if (selectedCategory === 'supporting-actors') {
      return (
        <div key={index} className="nominee-card">
          <div className="nominee-title">
            <div className="nominee-title-text">{highlightText(item, debouncedSearchTerm)}</div>
          </div>
        </div>
      );
    }

    if (selectedCategory === 'films') {
      return renderFilmCard(item);
    }

    const itemId = `${item.song || item.title || item.name}-${item.movie || item.director || ''}`;
    const isWatched = watchedItems[selectedCategory].has(itemId);

    return (
      <div key={item.id || index} className="nominee-card">
        <div className="nominee-title">
          <div className="nominee-title-text">{highlightText(item.song || item.title, debouncedSearchTerm)}</div>
          <div className="watched-checkbox" onClick={() => toggleWatched(itemId, selectedCategory)}>
            <span className={`checkbox ${isWatched ? 'checked' : ''}`}>
              {isWatched ? '✓' : ''}
            </span>
            <span className="watched-text">{selectedCategory === 'audition-films' ? '聽過' : '睇過'}</span>
          </div>
        </div>
        {item.fullTitle && item.fullTitle !== item.title && (
          <div className="nominee-subtitle" onClick={() => handleYouTubeSearch(item.fullTitle)}>
            <img src={youtubeIcon} alt="YouTube" className="youtube-icon" />
            {highlightText(item.fullTitle, debouncedSearchTerm)}
          </div>
        )}
        {item.movie && (
          <div className="nominee-movie">{highlightText(item.movie, debouncedSearchTerm)}</div>
        )}
        {item.director && (
          <div className="nominee-director">導演：{highlightText(item.director, debouncedSearchTerm)}</div>
        )}
        <div className="nominee-date">{item.releaseDate}</div>
      </div>
    );
  }, [selectedCategory, highlightText, debouncedSearchTerm, watchedItems, toggleWatched, renderFilmCard, handleYouTubeSearch]);

  return (
    <div className="app">
      <header className="app-header">
        <img src={headerImage} alt="試當真白金像獎" className="header-image" />
      </header>

      <div className="search-container">
        <input
          type="text"
          placeholder="搜尋候選作品..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
      </div>

      <div className="category-tabs">
        {categories.map((category) => (
          <button
            key={category.id}
            className={`category-tab ${selectedCategory === category.id ? 'active' : ''}`}
            onClick={() => setSelectedCategory(category.id)}
          >
            <span className="category-name">{category.name}</span>
          </button>
        ))}
      </div>

      <div className="nominees-container">
        {selectedCategory !== 'supporting-actors' && (
          <div className="watched-counter">
            <span className="counter-text">
              {selectedCategory === 'audition-films' 
                ? `聽過 ${watchedItems[selectedCategory].size} 首歌` 
                : `睇過 ${watchedItems[selectedCategory].size} 條片`
              }
            </span>
          </div>
        )}
        
        {selectedCategory === 'films' && debouncedSearchTerm && (
          <div className="search-results-counter">
            <span className="counter-text">
              揾{filteredData.length}條片
            </span>
          </div>
        )}
        
        <div className="disclaimer">
          <p>此網站僅供參考，請以 <a href="https://www.instagram.com/p/DMR3OmuTTR7" target="_blank" rel="noopener noreferrer">試當真IG</a>為準。</p>
        </div>
        
        {isLoading && selectedCategory === 'films' && (
          <div className="loading">
            <div className="loading-spinner"></div>
            <span>搜尋中...</span>
          </div>
        )}
        
        {selectedCategory === 'films' ? (
          <div 
            ref={filmsContainerRef}
            className="films-virtual-container"
            style={{ height: filmsContainerHeight, overflow: 'auto' }}
            onScroll={handleFilmsScroll}
          >
            <div style={{ height: filmsTotalHeight, position: 'relative' }}>
              <div style={{ transform: `translateY(${filmsOffsetY}px)` }}>
                {visibleFilms.map((item) => renderFilmCard(item))}
              </div>
            </div>
            {hasMore && (
              <div className="load-more-indicator">
                <div className="loading-spinner"></div>
                <span>載入更多...</span>
              </div>
            )}
          </div>
        ) : (
          <div className={`nominees-grid ${selectedCategory === 'films' ? 'films-grid' : ''}`}>
            {filteredData.map((item, index) => renderNomineeCard(item, index))}
          </div>
        )}
        
        {filteredData.length === 0 && !isLoading && (
          <div className="no-results">
            揾唔到
          </div>
        )}
      </div>
    </div>
  );
};

export default App;

