---
title: Resources
permalink: /resources/
layout: page
excerpt: A curated collection of web references, developer tools, design utilities, and content creation tools.
---

<div class="resources-controls">
  <div class="resources-search-wrapper">
    <span class="search-icon">
      <i class="bi bi-search" aria-hidden="true"></i>
    </span>
    <input 
      type="search" 
      id="resources-search" 
      placeholder="Search resources by name, description, or tags..." 
      aria-label="Search resources"
      autocomplete="off"
    >
  </div>
  
  <div class="resources-categories" id="resources-categories">
    <button type="button" class="category-btn is-active" data-category="all">All</button>
    <button type="button" class="category-btn" data-category="coding">Coding & Dev</button>
    <button type="button" class="category-btn" data-category="design">Design & UI</button>
    <button type="button" class="category-btn" data-category="media">Media & Video</button>
    <button type="button" class="category-btn" data-category="writing">Writing & Docs</button>
    <button type="button" class="category-btn" data-category="a11y">Web & A11y</button>
    <button type="button" class="category-btn" data-category="social">Socials & Profiles</button>
  </div>
</div>

<div id="resources-empty-state" class="resources-not-found" role="status" aria-live="polite" aria-atomic="true" hidden>
  <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" class="bi bi-search-heart" viewBox="0 0 16 16">
    <path d="M6.5 4.482c1.664-1.673 5.825 1.254 0 5.018-5.825-3.764-1.664-6.69 0-5.018"/>
    <path d="M13 6.5a6.47 6.47 0 0 1-1.258 3.844q.06.044.115.098l3.85 3.85a1 1 0 0 1-1.414 1.415l-3.85-3.85a1 1 0 0 1-.1-.115h.002A6.5 6.5 0 1 1 13 6.5M6.5 12a5.5 5.5 0 1 0 0-11 5.5 5.5 0 0 0 0 11"/>
  </svg>
  <p>No resources found matching your search</p>
</div>

<div class="resources-grid" id="resources-grid">
  {%- for item in site.data.resources -%}
    <a href="{{ item.url }}" class="resource-card" target="_blank" rel="noopener" data-category="{{ item.category }}">
      <div class="resource-header">
        <div class="resource-icon-wrapper">
          <i class="{{ item.icon }}" aria-hidden="true"></i>
        </div>
        <h3 class="resource-name">{{ item.name }}</h3>
        <i class="bi bi-arrow-up-right resource-arrow" aria-hidden="true"></i>
      </div>
      <p class="resource-desc">{{ item.description }}</p>
      <div class="resource-tags">
        {%- for tag in item.tags -%}
          <span class="resource-tag">{{ tag }}</span>
        {%- endfor -%}
      </div>
    </a>
  {%- endfor -%}
</div>
