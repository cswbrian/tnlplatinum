import React, { useState, useEffect } from 'react';
import './App.css';
import headerImage from './assets/header-min.png';
import songsData from './data/songs.json';
import adsData from './data/ads.json';
import supportingActorsData from './data/supporting-actors.json';
import varietyShowsData from './data/variety-shows.json';
import auditionFilmsData from './data/audition-films.json';
import filmsData from './data/films.json';

const App: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState<string>('films');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [watchedItems, setWatchedItems] = useState<Record<string, Set<string>>>({
    films: new Set(),
    songs: new Set(),
    ads: new Set(),
    'audition-films': new Set(),
    'variety-shows': new Set(),
    'supporting-actors': new Set()
  });

  // Helper function to highlight searched text
  const highlightText = (text: string, searchTerm: string) => {
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
  };

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

  const toggleWatched = (itemId: string, category: string) => {
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
  };

  const categories = [
    { id: 'films', name: '最佳電影', data: filmsData, count: filmsData.length },
    { id: 'songs', name: '最佳原創電影歌曲', data: songsData, count: songsData.length },
    { id: 'ads', name: '最佳廣告片', data: adsData, count: adsData.length },
    { id: 'audition-films', name: '最佳試音片', data: auditionFilmsData, count: auditionFilmsData.length },
    { id: 'variety-shows', name: '最佳綜藝', data: varietyShowsData, count: varietyShowsData.length },
    { id: 'supporting-actors', name: '最佳搭膊頭', data: supportingActorsData, count: supportingActorsData.length },
  ];

  const currentCategory = categories.find(cat => cat.id === selectedCategory);
  const filteredData = currentCategory?.data.filter((item: any) => {
    if (selectedCategory === 'supporting-actors') {
      return item.toLowerCase().includes(searchTerm.toLowerCase());
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
        field.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    const searchFields = [
      item.title || item.song || item.name,
      item.fullTitle,
      item.movie,
      item.director
    ].filter(Boolean);
    return searchFields.some(field => 
      field.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }) || [];

    const renderFilmCard = (item: any, index: number) => {
    const filmId = `${item.title}-${item.director || ''}`;
    const isWatched = watchedItems.films.has(filmId);
    
    return (
      <div key={index} className="nominee-card film-card">
        <div className="nominee-title">
          {highlightText(item.title, searchTerm)}
          <div className="watched-checkbox" onClick={() => toggleWatched(filmId, 'films')}>
            <span className={`checkbox ${isWatched ? 'checked' : ''}`}>
              {isWatched ? '✓' : ''}
            </span>
            <span className="watched-text">睇過</span>
          </div>
        </div>
        {item.fullTitle && item.fullTitle !== item.title && (
          <div className="nominee-subtitle">{highlightText(item.fullTitle, searchTerm)}</div>
        )}
        
        <div className="film-details">
          {item.director && (
            <div className="film-detail">
              <span className="detail-label">導演：</span>
              <span className="detail-value">{highlightText(item.director, searchTerm)}</span>
            </div>
          )}
          {item.writer && (
            <div className="film-detail">
              <span className="detail-label">編劇：</span>
              <span className="detail-value">{highlightText(item.writer, searchTerm)}</span>
            </div>
          )}
          {item.leadActor && (
            <div className="film-detail">
              <span className="detail-label">男主角：</span>
              <span className="detail-value">{highlightText(item.leadActor, searchTerm)}</span>
            </div>
          )}
          {item.leadActress && (
            <div className="film-detail">
              <span className="detail-label">女主角：</span>
              <span className="detail-value">{highlightText(item.leadActress, searchTerm)}</span>
            </div>
          )}
          {item.supportingActor && (
            <div className="film-detail">
              <span className="detail-label">男配角：</span>
              <span className="detail-value">{highlightText(item.supportingActor, searchTerm)}</span>
            </div>
          )}
          {item.supportingActress && (
            <div className="film-detail">
              <span className="detail-label">女配角：</span>
              <span className="detail-value">{highlightText(item.supportingActress, searchTerm)}</span>
            </div>
          )}
          {item.newActor && (
            <div className="film-detail">
              <span className="detail-label">新演員：</span>
              <span className="detail-value">{highlightText(item.newActor, searchTerm)}</span>
            </div>
          )}
          {item.editor && (
            <div className="film-detail">
              <span className="detail-label">剪接：</span>
              <span className="detail-value">{highlightText(item.editor, searchTerm)}</span>
            </div>
          )}
          {item.cinematographer && (
            <div className="film-detail">
              <span className="detail-label">攝影：</span>
              <span className="detail-value">{highlightText(item.cinematographer, searchTerm)}</span>
            </div>
          )}
          {item.actionDesign && (
            <div className="film-detail">
              <span className="detail-label">動作設計：</span>
              <span className="detail-value">{highlightText(item.actionDesign, searchTerm)}</span>
            </div>
          )}
          {item.artDirector && (
            <div className="film-detail">
              <span className="detail-label">美術指導：</span>
              <span className="detail-value">{highlightText(item.artDirector, searchTerm)}</span>
            </div>
          )}
          {item.visualEffects && (
            <div className="film-detail">
              <span className="detail-label">視覺效果：</span>
              <span className="detail-value">{highlightText(item.visualEffects, searchTerm)}</span>
            </div>
          )}
        </div>
        
        <div className="film-meta">
          {item.releaseDate && (
            <span className="film-date">{item.releaseDate}</span>
          )}
        </div>
      </div>
    );
  };

  const renderNomineeCard = (item: any, index: number) => {
    if (selectedCategory === 'supporting-actors') {
      return (
        <div key={index} className="nominee-card">
          <div className="nominee-title">
            {highlightText(item, searchTerm)}
          </div>
        </div>
      );
    }

    if (selectedCategory === 'films') {
      return renderFilmCard(item, index);
    }

    const itemId = `${item.song || item.title || item.name}-${item.movie || item.director || ''}`;
    const isWatched = watchedItems[selectedCategory].has(itemId);

    return (
      <div key={item.id || index} className="nominee-card">
        <div className="nominee-title">
          {highlightText(item.song || item.title, searchTerm)}
          <div className="watched-checkbox" onClick={() => toggleWatched(itemId, selectedCategory)}>
            <span className={`checkbox ${isWatched ? 'checked' : ''}`}>
              {isWatched ? '✓' : ''}
            </span>
            <span className="watched-text">{selectedCategory === 'audition-films' ? '聽過' : '睇過'}</span>
          </div>
        </div>
        {item.fullTitle && item.fullTitle !== item.title && (
          <div className="nominee-subtitle">{highlightText(item.fullTitle, searchTerm)}</div>
        )}
        {item.movie && (
          <div className="nominee-movie">電影：{highlightText(item.movie, searchTerm)}</div>
        )}
        {item.director && (
          <div className="nominee-director">導演：{highlightText(item.director, searchTerm)}</div>
        )}
        <div className="nominee-date">{item.releaseDate}</div>
      </div>
    );
  };

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
        <div className="disclaimer">
          <p>此網站僅供參考，請以 <a href="https://www.instagram.com/p/DMR3OmuTTR7" target="_blank" rel="noopener noreferrer">試當真IG</a>為準。</p>
        </div>
        
        <div className={`nominees-grid ${selectedCategory === 'films' ? 'films-grid' : ''}`}>
          {filteredData.map((item, index) => renderNomineeCard(item, index))}
        </div>
        {filteredData.length === 0 && (
          <div className="no-results">
            沒有找到符合搜尋條件的結果
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
