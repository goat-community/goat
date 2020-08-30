




<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
  <link rel="dns-prefetch" href="https://github.githubassets.com">
  <link rel="dns-prefetch" href="https://avatars0.githubusercontent.com">
  <link rel="dns-prefetch" href="https://avatars1.githubusercontent.com">
  <link rel="dns-prefetch" href="https://avatars2.githubusercontent.com">
  <link rel="dns-prefetch" href="https://avatars3.githubusercontent.com">
  <link rel="dns-prefetch" href="https://github-cloud.s3.amazonaws.com">
  <link rel="dns-prefetch" href="https://user-images.githubusercontent.com/">



  <link crossorigin="anonymous" media="all" integrity="sha512-jFUBCdWOA1Ov3xo3oFMBwsdP4Up2K1bRnP4QYI5WqvpaIYxWVek89k2M0oyTbNhYMViGtxJB3Vdwcw8ln8hGQw==" rel="stylesheet" href="https://github.githubassets.com/assets/frameworks-8c550109d58e0353afdf1a37a05301c2.css" />
  
    <link crossorigin="anonymous" media="all" integrity="sha512-fN8XiTy3uS/0K6pumB0JFrrZoLpai1AuRyZBoLm6tH8i4nngYoTN6IUR7x6aegFVHtn8w9ave0QRggWKozu7BQ==" rel="stylesheet" href="https://github.githubassets.com/assets/github-7cdf17893cb7b92ff42baa6e981d0916.css" />
    
    
    
    


  <meta name="viewport" content="width=device-width">
  
  <title>goat/pois.sql at main · goat-community/goat</title>
    <meta name="description" content="This is the home of Geo Open Accessibility Tool (GOAT) - goat-community/goat">
    <link rel="search" type="application/opensearchdescription+xml" href="/opensearch.xml" title="GitHub">
  <link rel="fluid-icon" href="https://github.com/fluidicon.png" title="GitHub">
  <meta property="fb:app_id" content="1401488693436528">
  <meta name="apple-itunes-app" content="app-id=1477376905">

    <meta name="twitter:image:src" content="https://avatars3.githubusercontent.com/u/58163984?s=400&amp;v=4" /><meta name="twitter:site" content="@github" /><meta name="twitter:card" content="summary" /><meta name="twitter:title" content="goat-community/goat" /><meta name="twitter:description" content="This is the home of Geo Open Accessibility Tool (GOAT) - goat-community/goat" />
    <meta property="og:image" content="https://avatars3.githubusercontent.com/u/58163984?s=400&amp;v=4" /><meta property="og:site_name" content="GitHub" /><meta property="og:type" content="object" /><meta property="og:title" content="goat-community/goat" /><meta property="og:url" content="https://github.com/goat-community/goat" /><meta property="og:description" content="This is the home of Geo Open Accessibility Tool (GOAT) - goat-community/goat" />



  

  <link rel="assets" href="https://github.githubassets.com/">
    <link rel="shared-web-socket" href="wss://alive.github.com/_sockets/u/58067217/ws?session=eyJ2IjoiVjMiLCJ1Ijo1ODA2NzIxNywicyI6NDk5MDAzNTEyLCJjIjo1MjAyNjY4MzIsInQiOjE1OTg3OTU2NjN9--323573c6b88ca75cd31611092de96bbf9ea5c66de94b9b4a83f9b83968b8aa01" data-refresh-url="/_ws">
  <link rel="sudo-modal" href="/sessions/sudo_modal">

  <meta name="request-id" content="C9C2:BC7E:11BB011:195E722:5F4BAF8C" data-pjax-transient="true" /><meta name="html-safe-nonce" content="6c948c1d80cab61c1c6116083f4de3e3a21e3334" data-pjax-transient="true" /><meta name="visitor-payload" content="eyJyZWZlcnJlciI6Imh0dHBzOi8vZ2l0aHViLmNvbS9nb2F0LWNvbW11bml0eS9nb2F0L3RyZWUvbWFpbi9hcHAvZGF0YWJhc2UvZGF0YV9wcmVwYXJhdGlvbi9TUUwiLCJyZXF1ZXN0X2lkIjoiQzlDMjpCQzdFOjExQkIwMTE6MTk1RTcyMjo1RjRCQUY4QyIsInZpc2l0b3JfaWQiOiI3MTY3NzMzNTk0NTgzMTUzMTIxIiwicmVnaW9uX2VkZ2UiOiJmcmEiLCJyZWdpb25fcmVuZGVyIjoiaWFkIn0=" data-pjax-transient="true" /><meta name="visitor-hmac" content="a7aa7d816c97a0bfb947d5d35a5acd0c46601744be826286facf0bf46e8ad93f" data-pjax-transient="true" /><meta name="cookie-consent-required" content="true" />

    <meta name="hovercard-subject-tag" content="repository:150960118" data-pjax-transient>


  <meta name="github-keyboard-shortcuts" content="repository,source-code" data-pjax-transient="true" />

  

  <meta name="selected-link" value="repo_source" data-pjax-transient>

    <meta name="google-site-verification" content="c1kuD-K2HIVF635lypcsWPoD4kilo5-jA_wBFyT4uMY">
  <meta name="google-site-verification" content="KT5gs8h0wvaagLKAVWq8bbeNwnZZK1r1XQysX3xurLU">
  <meta name="google-site-verification" content="ZzhVyEFwb7w3e0-uOTltm8Jsck2F5StVihD0exw2fsA">
  <meta name="google-site-verification" content="GXs5KoUUkNCoaAZn7wPN-t01Pywp9M3sEjnt_3_ZWPc">

  <meta name="octolytics-host" content="collector.githubapp.com" /><meta name="octolytics-app-id" content="github" /><meta name="octolytics-event-url" content="https://collector.githubapp.com/github-external/browser_event" /><meta name="octolytics-dimension-ga_id" content="" class="js-octo-ga-id" /><meta name="octolytics-actor-id" content="58067217" /><meta name="octolytics-actor-login" content="rafleo2008" /><meta name="octolytics-actor-hash" content="f87678a6c0eb09fb4b1fe139a5fe1d15d2ff3062334a5eb6b903d1d3abd51c68" />

  <meta name="analytics-location" content="/&lt;user-name&gt;/&lt;repo-name&gt;/blob/show" data-pjax-transient="true" />

  





    <meta name="google-analytics" content="UA-3769691-2">

  <meta class="js-ga-set" name="userId" content="e489e6f5c83a20a0e261996da2f26865">

<meta class="js-ga-set" name="dimension10" content="Responsive" data-pjax-transient>

<meta class="js-ga-set" name="dimension1" content="Logged In">



  

      <meta name="hostname" content="github.com">
    <meta name="user-login" content="rafleo2008">


      <meta name="expected-hostname" content="github.com">

      <meta name="js-proxy-site-detection-payload" content="ZGRkNDhjMjE1YTAxYjIxNjA0YTExZmIwOWZlODVkNDVhOGI4MzFjNTM4OWM1MGU3NmIxZjBiM2UxYTk5MTI2NXx7InJlbW90ZV9hZGRyZXNzIjoiMTM4LjI0Ni4yLjEyNCIsInJlcXVlc3RfaWQiOiJDOUMyOkJDN0U6MTFCQjAxMToxOTVFNzIyOjVGNEJBRjhDIiwidGltZXN0YW1wIjoxNTk4Nzk1NjYzLCJob3N0IjoiZ2l0aHViLmNvbSJ9">

    <meta name="enabled-features" content="MARKETPLACE_PENDING_INSTALLATIONS,JS_HTTP_CACHE_HEADERS">

  <meta http-equiv="x-pjax-version" content="8687ed860896fc34d37f552a217bbb09">
  

      <link href="https://github.com/goat-community/goat/commits/main.atom" rel="alternate" title="Recent Commits to goat:main" type="application/atom+xml">

  <meta name="go-import" content="github.com/goat-community/goat git https://github.com/goat-community/goat.git">

  <meta name="octolytics-dimension-user_id" content="58163984" /><meta name="octolytics-dimension-user_login" content="goat-community" /><meta name="octolytics-dimension-repository_id" content="150960118" /><meta name="octolytics-dimension-repository_nwo" content="goat-community/goat" /><meta name="octolytics-dimension-repository_public" content="true" /><meta name="octolytics-dimension-repository_is_fork" content="false" /><meta name="octolytics-dimension-repository_network_root_id" content="150960118" /><meta name="octolytics-dimension-repository_network_root_nwo" content="goat-community/goat" /><meta name="octolytics-dimension-repository_explore_github_marketplace_ci_cta_shown" content="false" />


    <link rel="canonical" href="https://github.com/goat-community/goat/blob/main/app/database/data_preparation/SQL/pois.sql" data-pjax-transient>


  <meta name="browser-stats-url" content="https://api.github.com/_private/browser/stats">

  <meta name="browser-errors-url" content="https://api.github.com/_private/browser/errors">

  <link rel="mask-icon" href="https://github.githubassets.com/pinned-octocat.svg" color="#000000">
  <link rel="alternate icon" class="js-site-favicon" type="image/png" href="https://github.githubassets.com/favicons/favicon.png">
  <link rel="icon" class="js-site-favicon" type="image/svg+xml" href="https://github.githubassets.com/favicons/favicon.svg">

<meta name="theme-color" content="#1e2327">


  <link rel="manifest" href="/manifest.json" crossOrigin="use-credentials">

  </head>

  <body class="logged-in env-production page-responsive page-blob">
    

    <input type="hidden" value="X7Y4vXACbPKIJ/Q+VQjldUQM/Z4gpdL6I2HrsNNAaRDw5muK8BEZV3yH9svJ5oE7ctIlYjRTmLnGDZh/BrCIxg==" data-csrf="true" class="js-data-websocket-refresh-csrf" />

    <div class="position-relative js-header-wrapper ">
      <a href="#start-of-content" class="p-3 bg-blue text-white show-on-focus js-skip-to-content">Skip to content</a>
      <span class="progress-pjax-loader width-full js-pjax-loader-bar Progress position-fixed">
    <span style="background-color: #79b8ff;width: 0%;" class="Progress-item progress-pjax-loader-bar "></span>
</span>      
      



          <header class="Header py-md-0 js-details-container Details flex-wrap flex-md-nowrap px-3" role="banner">
  <div class="Header-item d-none d-md-flex">
    <a class="Header-link" href="https://github.com/" data-hotkey="g d"
  aria-label="Homepage " data-ga-click="Header, go to dashboard, icon:logo">
  <svg class="octicon octicon-mark-github v-align-middle" height="32" viewBox="0 0 16 16" version="1.1" width="32" aria-hidden="true"><path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path></svg>
</a>

  </div>

  <div class="Header-item d-md-none">
    <button class="Header-link btn-link js-details-target" type="button" aria-label="Toggle navigation" aria-expanded="false">
      <svg height="24" class="octicon octicon-three-bars" viewBox="0 0 16 16" version="1.1" width="24" aria-hidden="true"><path fill-rule="evenodd" d="M1 2.75A.75.75 0 011.75 2h12.5a.75.75 0 110 1.5H1.75A.75.75 0 011 2.75zm0 5A.75.75 0 011.75 7h12.5a.75.75 0 110 1.5H1.75A.75.75 0 011 7.75zM1.75 12a.75.75 0 100 1.5h12.5a.75.75 0 100-1.5H1.75z"></path></svg>
    </button>
  </div>

  <div class="Header-item Header-item--full flex-column flex-md-row width-full flex-order-2 flex-md-order-none mr-0 mr-md-3 mt-3 mt-md-0 Details-content--hidden-not-important d-md-flex">
        <div class="header-search header-search-current js-header-search-current flex-auto  flex-self-stretch flex-md-self-auto mr-0 mr-md-3 mb-3 mb-md-0 scoped-search site-scoped-search js-site-search position-relative js-jump-to js-header-search-current-jump-to"
  role="combobox"
  aria-owns="jump-to-results"
  aria-label="Search or jump to"
  aria-haspopup="listbox"
  aria-expanded="false"
>
  <div class="position-relative">
    <!-- '"` --><!-- </textarea></xmp> --></option></form><form class="js-site-search-form" role="search" aria-label="Site" data-scope-type="Repository" data-scope-id="150960118" data-scoped-search-url="/goat-community/goat/search" data-unscoped-search-url="/search" action="/goat-community/goat/search" accept-charset="UTF-8" method="get">
      <label class="form-control input-sm header-search-wrapper p-0 header-search-wrapper-jump-to position-relative d-flex flex-justify-between flex-items-center js-chromeless-input-container">
        <input type="text"
          class="form-control input-sm header-search-input jump-to-field js-jump-to-field js-site-search-focus js-site-search-field is-clearable"
          data-hotkey="s,/"
          name="q"
          value=""
          placeholder="Search or jump to…"
          data-unscoped-placeholder="Search or jump to…"
          data-scoped-placeholder="Search or jump to…"
          autocapitalize="off"
          aria-autocomplete="list"
          aria-controls="jump-to-results"
          aria-label="Search or jump to…"
          data-jump-to-suggestions-path="/_graphql/GetSuggestedNavigationDestinations"
          spellcheck="false"
          autocomplete="off"
          >
          <input type="hidden" value="wQQMNgBOUqknLMshHQUSfSzG0EUHsnrG957PK2cMokdRal1K7YMT8+2/6hytoSBxCcdh/cPUznYVQeXWdfSEXA==" data-csrf="true" class="js-data-jump-to-suggestions-path-csrf" />
          <input type="hidden" class="js-site-search-type-field" name="type" >
            <img src="https://github.githubassets.com/images/search-key-slash.svg" alt="" class="mr-2 header-search-key-slash">

            <div class="Box position-absolute overflow-hidden d-none jump-to-suggestions js-jump-to-suggestions-container">
              
<ul class="d-none js-jump-to-suggestions-template-container">
  

<li class="d-flex flex-justify-start flex-items-center p-0 f5 navigation-item js-navigation-item js-jump-to-suggestion" role="option">
  <a tabindex="-1" class="no-underline d-flex flex-auto flex-items-center jump-to-suggestions-path js-jump-to-suggestion-path js-navigation-open p-2" href="">
    <div class="jump-to-octicon js-jump-to-octicon flex-shrink-0 mr-2 text-center d-none">
      <svg height="16" width="16" class="octicon octicon-repo flex-shrink-0 js-jump-to-octicon-repo d-none" title="Repository" aria-label="Repository" viewBox="0 0 16 16" version="1.1" role="img"><path fill-rule="evenodd" d="M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9zm10.5-1V9h-8c-.356 0-.694.074-1 .208V2.5a1 1 0 011-1h8zM5 12.25v3.25a.25.25 0 00.4.2l1.45-1.087a.25.25 0 01.3 0L8.6 15.7a.25.25 0 00.4-.2v-3.25a.25.25 0 00-.25-.25h-3.5a.25.25 0 00-.25.25z"></path></svg>
      <svg height="16" width="16" class="octicon octicon-project flex-shrink-0 js-jump-to-octicon-project d-none" title="Project" aria-label="Project" viewBox="0 0 16 16" version="1.1" role="img"><path fill-rule="evenodd" d="M1.75 0A1.75 1.75 0 000 1.75v12.5C0 15.216.784 16 1.75 16h12.5A1.75 1.75 0 0016 14.25V1.75A1.75 1.75 0 0014.25 0H1.75zM1.5 1.75a.25.25 0 01.25-.25h12.5a.25.25 0 01.25.25v12.5a.25.25 0 01-.25.25H1.75a.25.25 0 01-.25-.25V1.75zM11.75 3a.75.75 0 00-.75.75v7.5a.75.75 0 001.5 0v-7.5a.75.75 0 00-.75-.75zm-8.25.75a.75.75 0 011.5 0v5.5a.75.75 0 01-1.5 0v-5.5zM8 3a.75.75 0 00-.75.75v3.5a.75.75 0 001.5 0v-3.5A.75.75 0 008 3z"></path></svg>
      <svg height="16" width="16" class="octicon octicon-search flex-shrink-0 js-jump-to-octicon-search d-none" title="Search" aria-label="Search" viewBox="0 0 16 16" version="1.1" role="img"><path fill-rule="evenodd" d="M11.5 7a4.499 4.499 0 11-8.998 0A4.499 4.499 0 0111.5 7zm-.82 4.74a6 6 0 111.06-1.06l3.04 3.04a.75.75 0 11-1.06 1.06l-3.04-3.04z"></path></svg>
    </div>

    <img class="avatar mr-2 flex-shrink-0 js-jump-to-suggestion-avatar d-none" alt="" aria-label="Team" src="" width="28" height="28">

    <div class="jump-to-suggestion-name js-jump-to-suggestion-name flex-auto overflow-hidden text-left no-wrap css-truncate css-truncate-target">
    </div>

    <div class="border rounded-1 flex-shrink-0 bg-gray px-1 text-gray-light ml-1 f6 d-none js-jump-to-badge-search">
      <span class="js-jump-to-badge-search-text-default d-none" aria-label="in this repository">
        In this repository
      </span>
      <span class="js-jump-to-badge-search-text-global d-none" aria-label="in all of GitHub">
        All GitHub
      </span>
      <span aria-hidden="true" class="d-inline-block ml-1 v-align-middle">↵</span>
    </div>

    <div aria-hidden="true" class="border rounded-1 flex-shrink-0 bg-gray px-1 text-gray-light ml-1 f6 d-none d-on-nav-focus js-jump-to-badge-jump">
      Jump to
      <span class="d-inline-block ml-1 v-align-middle">↵</span>
    </div>
  </a>
</li>

</ul>

<ul class="d-none js-jump-to-no-results-template-container">
  <li class="d-flex flex-justify-center flex-items-center f5 d-none js-jump-to-suggestion p-2">
    <span class="text-gray">No suggested jump to results</span>
  </li>
</ul>

<ul id="jump-to-results" role="listbox" class="p-0 m-0 js-navigation-container jump-to-suggestions-results-container js-jump-to-suggestions-results-container">
  

<li class="d-flex flex-justify-start flex-items-center p-0 f5 navigation-item js-navigation-item js-jump-to-scoped-search d-none" role="option">
  <a tabindex="-1" class="no-underline d-flex flex-auto flex-items-center jump-to-suggestions-path js-jump-to-suggestion-path js-navigation-open p-2" href="">
    <div class="jump-to-octicon js-jump-to-octicon flex-shrink-0 mr-2 text-center d-none">
      <svg height="16" width="16" class="octicon octicon-repo flex-shrink-0 js-jump-to-octicon-repo d-none" title="Repository" aria-label="Repository" viewBox="0 0 16 16" version="1.1" role="img"><path fill-rule="evenodd" d="M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9zm10.5-1V9h-8c-.356 0-.694.074-1 .208V2.5a1 1 0 011-1h8zM5 12.25v3.25a.25.25 0 00.4.2l1.45-1.087a.25.25 0 01.3 0L8.6 15.7a.25.25 0 00.4-.2v-3.25a.25.25 0 00-.25-.25h-3.5a.25.25 0 00-.25.25z"></path></svg>
      <svg height="16" width="16" class="octicon octicon-project flex-shrink-0 js-jump-to-octicon-project d-none" title="Project" aria-label="Project" viewBox="0 0 16 16" version="1.1" role="img"><path fill-rule="evenodd" d="M1.75 0A1.75 1.75 0 000 1.75v12.5C0 15.216.784 16 1.75 16h12.5A1.75 1.75 0 0016 14.25V1.75A1.75 1.75 0 0014.25 0H1.75zM1.5 1.75a.25.25 0 01.25-.25h12.5a.25.25 0 01.25.25v12.5a.25.25 0 01-.25.25H1.75a.25.25 0 01-.25-.25V1.75zM11.75 3a.75.75 0 00-.75.75v7.5a.75.75 0 001.5 0v-7.5a.75.75 0 00-.75-.75zm-8.25.75a.75.75 0 011.5 0v5.5a.75.75 0 01-1.5 0v-5.5zM8 3a.75.75 0 00-.75.75v3.5a.75.75 0 001.5 0v-3.5A.75.75 0 008 3z"></path></svg>
      <svg height="16" width="16" class="octicon octicon-search flex-shrink-0 js-jump-to-octicon-search d-none" title="Search" aria-label="Search" viewBox="0 0 16 16" version="1.1" role="img"><path fill-rule="evenodd" d="M11.5 7a4.499 4.499 0 11-8.998 0A4.499 4.499 0 0111.5 7zm-.82 4.74a6 6 0 111.06-1.06l3.04 3.04a.75.75 0 11-1.06 1.06l-3.04-3.04z"></path></svg>
    </div>

    <img class="avatar mr-2 flex-shrink-0 js-jump-to-suggestion-avatar d-none" alt="" aria-label="Team" src="" width="28" height="28">

    <div class="jump-to-suggestion-name js-jump-to-suggestion-name flex-auto overflow-hidden text-left no-wrap css-truncate css-truncate-target">
    </div>

    <div class="border rounded-1 flex-shrink-0 bg-gray px-1 text-gray-light ml-1 f6 d-none js-jump-to-badge-search">
      <span class="js-jump-to-badge-search-text-default d-none" aria-label="in this repository">
        In this repository
      </span>
      <span class="js-jump-to-badge-search-text-global d-none" aria-label="in all of GitHub">
        All GitHub
      </span>
      <span aria-hidden="true" class="d-inline-block ml-1 v-align-middle">↵</span>
    </div>

    <div aria-hidden="true" class="border rounded-1 flex-shrink-0 bg-gray px-1 text-gray-light ml-1 f6 d-none d-on-nav-focus js-jump-to-badge-jump">
      Jump to
      <span class="d-inline-block ml-1 v-align-middle">↵</span>
    </div>
  </a>
</li>

  

<li class="d-flex flex-justify-start flex-items-center p-0 f5 navigation-item js-navigation-item js-jump-to-global-search d-none" role="option">
  <a tabindex="-1" class="no-underline d-flex flex-auto flex-items-center jump-to-suggestions-path js-jump-to-suggestion-path js-navigation-open p-2" href="">
    <div class="jump-to-octicon js-jump-to-octicon flex-shrink-0 mr-2 text-center d-none">
      <svg height="16" width="16" class="octicon octicon-repo flex-shrink-0 js-jump-to-octicon-repo d-none" title="Repository" aria-label="Repository" viewBox="0 0 16 16" version="1.1" role="img"><path fill-rule="evenodd" d="M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9zm10.5-1V9h-8c-.356 0-.694.074-1 .208V2.5a1 1 0 011-1h8zM5 12.25v3.25a.25.25 0 00.4.2l1.45-1.087a.25.25 0 01.3 0L8.6 15.7a.25.25 0 00.4-.2v-3.25a.25.25 0 00-.25-.25h-3.5a.25.25 0 00-.25.25z"></path></svg>
      <svg height="16" width="16" class="octicon octicon-project flex-shrink-0 js-jump-to-octicon-project d-none" title="Project" aria-label="Project" viewBox="0 0 16 16" version="1.1" role="img"><path fill-rule="evenodd" d="M1.75 0A1.75 1.75 0 000 1.75v12.5C0 15.216.784 16 1.75 16h12.5A1.75 1.75 0 0016 14.25V1.75A1.75 1.75 0 0014.25 0H1.75zM1.5 1.75a.25.25 0 01.25-.25h12.5a.25.25 0 01.25.25v12.5a.25.25 0 01-.25.25H1.75a.25.25 0 01-.25-.25V1.75zM11.75 3a.75.75 0 00-.75.75v7.5a.75.75 0 001.5 0v-7.5a.75.75 0 00-.75-.75zm-8.25.75a.75.75 0 011.5 0v5.5a.75.75 0 01-1.5 0v-5.5zM8 3a.75.75 0 00-.75.75v3.5a.75.75 0 001.5 0v-3.5A.75.75 0 008 3z"></path></svg>
      <svg height="16" width="16" class="octicon octicon-search flex-shrink-0 js-jump-to-octicon-search d-none" title="Search" aria-label="Search" viewBox="0 0 16 16" version="1.1" role="img"><path fill-rule="evenodd" d="M11.5 7a4.499 4.499 0 11-8.998 0A4.499 4.499 0 0111.5 7zm-.82 4.74a6 6 0 111.06-1.06l3.04 3.04a.75.75 0 11-1.06 1.06l-3.04-3.04z"></path></svg>
    </div>

    <img class="avatar mr-2 flex-shrink-0 js-jump-to-suggestion-avatar d-none" alt="" aria-label="Team" src="" width="28" height="28">

    <div class="jump-to-suggestion-name js-jump-to-suggestion-name flex-auto overflow-hidden text-left no-wrap css-truncate css-truncate-target">
    </div>

    <div class="border rounded-1 flex-shrink-0 bg-gray px-1 text-gray-light ml-1 f6 d-none js-jump-to-badge-search">
      <span class="js-jump-to-badge-search-text-default d-none" aria-label="in this repository">
        In this repository
      </span>
      <span class="js-jump-to-badge-search-text-global d-none" aria-label="in all of GitHub">
        All GitHub
      </span>
      <span aria-hidden="true" class="d-inline-block ml-1 v-align-middle">↵</span>
    </div>

    <div aria-hidden="true" class="border rounded-1 flex-shrink-0 bg-gray px-1 text-gray-light ml-1 f6 d-none d-on-nav-focus js-jump-to-badge-jump">
      Jump to
      <span class="d-inline-block ml-1 v-align-middle">↵</span>
    </div>
  </a>
</li>


    <li class="d-flex flex-justify-center flex-items-center p-0 f5 js-jump-to-suggestion">
      <img src="https://github.githubassets.com/images/spinners/octocat-spinner-128.gif" alt="Octocat Spinner Icon" class="m-2" width="28">
    </li>
</ul>

            </div>
      </label>
</form>  </div>
</div>


    <nav class="d-flex flex-column flex-md-row flex-self-stretch flex-md-self-auto" aria-label="Global">
    <a class="Header-link py-md-3 d-block d-md-none py-2 border-top border-md-top-0 border-white-fade-15" data-ga-click="Header, click, Nav menu - item:dashboard:user" aria-label="Dashboard" href="/dashboard">
      Dashboard
</a>
  <a class="js-selected-navigation-item Header-link py-md-3  mr-0 mr-md-3 py-2 border-top border-md-top-0 border-white-fade-15" data-hotkey="g p" data-ga-click="Header, click, Nav menu - item:pulls context:user" aria-label="Pull requests you created" data-selected-links="/pulls /pulls/assigned /pulls/mentioned /pulls" href="/pulls">
      Pull<span class="d-inline d-md-none d-lg-inline"> request</span>s
</a>
  <a class="js-selected-navigation-item Header-link py-md-3  mr-0 mr-md-3 py-2 border-top border-md-top-0 border-white-fade-15" data-hotkey="g i" data-ga-click="Header, click, Nav menu - item:issues context:user" aria-label="Issues you created" data-selected-links="/issues /issues/assigned /issues/mentioned /issues" href="/issues">
    Issues
</a>

    <div class="mr-0 mr-md-3 py-2 py-md-0 border-top border-md-top-0 border-white-fade-15">
      <a class="js-selected-navigation-item Header-link py-md-3 d-inline-block" data-ga-click="Header, click, Nav menu - item:marketplace context:user" data-octo-click="marketplace_click" data-octo-dimensions="location:nav_bar" data-selected-links=" /marketplace" href="/marketplace">
        Marketplace
</a>      

    </div>

  <a class="js-selected-navigation-item Header-link py-md-3  mr-0 mr-md-3 py-2 border-top border-md-top-0 border-white-fade-15" data-ga-click="Header, click, Nav menu - item:explore" data-selected-links="/explore /trending /trending/developers /integrations /integrations/feature/code /integrations/feature/collaborate /integrations/feature/ship showcases showcases_search showcases_landing /explore" href="/explore">
    Explore
</a>


    <a class="Header-link d-block d-md-none mr-0 mr-md-3 py-2 py-md-3 border-top border-md-top-0 border-white-fade-15" href="/rafleo2008">
      <img class="avatar avatar-user" src="https://avatars2.githubusercontent.com/u/58067217?s=40&amp;v=4" width="20" height="20" alt="@rafleo2008" />
      rafleo2008
</a>
    <!-- '"` --><!-- </textarea></xmp> --></option></form><form action="/logout" accept-charset="UTF-8" method="post"><input type="hidden" name="authenticity_token" value="BqTOSu4+7DBQeLGyeo1XtMO+j3xmd84poZLzOqOzhXPee2ynRrODgs7JE4I36v02I4G7jQdlLj43rhr7sNVnww==" />
      <button type="submit" class="Header-link mr-0 mr-md-3 py-2 py-md-3 border-top border-md-top-0 border-white-fade-15 d-md-none btn-link d-block width-full text-left" data-ga-click="Header, sign out, icon:logout" style="padding-left: 2px;">
        <svg class="octicon octicon-sign-out v-align-middle" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M2 2.75C2 1.784 2.784 1 3.75 1h2.5a.75.75 0 010 1.5h-2.5a.25.25 0 00-.25.25v10.5c0 .138.112.25.25.25h2.5a.75.75 0 010 1.5h-2.5A1.75 1.75 0 012 13.25V2.75zm10.44 4.5H6.75a.75.75 0 000 1.5h5.69l-1.97 1.97a.75.75 0 101.06 1.06l3.25-3.25a.75.75 0 000-1.06l-3.25-3.25a.75.75 0 10-1.06 1.06l1.97 1.97z"></path></svg>
        Sign out
      </button>
</form></nav>

  </div>

  <div class="Header-item Header-item--full flex-justify-center d-md-none position-relative">
    <a class="Header-link" href="https://github.com/" data-hotkey="g d"
  aria-label="Homepage " data-ga-click="Header, go to dashboard, icon:logo">
  <svg class="octicon octicon-mark-github v-align-middle" height="32" viewBox="0 0 16 16" version="1.1" width="32" aria-hidden="true"><path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path></svg>
</a>

  </div>

  <div class="Header-item mr-0 mr-md-3 flex-order-1 flex-md-order-none">
    

    <notification-indicator class="js-socket-channel" data-channel="eyJjIjoibm90aWZpY2F0aW9uLWNoYW5nZWQ6NTgwNjcyMTciLCJ0IjoxNTk4Nzk1NjYzfQ==--8d87f24ec8c786b30164cbecef6e0e43a152079e8d905d2fda6dc7bfc121fe18">
      <a href="/notifications"
         class="Header-link notification-indicator position-relative tooltipped tooltipped-sw"
         aria-label="You have no unread notifications"
         data-hotkey="g n"
         data-ga-click="Header, go to notifications, icon:read"
         data-target="notification-indicator.link">
         <span class="mail-status " data-target="notification-indicator.modifier"></span>
         <svg class="octicon octicon-bell" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path d="M8 16a2 2 0 001.985-1.75c.017-.137-.097-.25-.235-.25h-3.5c-.138 0-.252.113-.235.25A2 2 0 008 16z"></path><path fill-rule="evenodd" d="M8 1.5A3.5 3.5 0 004.5 5v2.947c0 .346-.102.683-.294.97l-1.703 2.556a.018.018 0 00-.003.01l.001.006c0 .002.002.004.004.006a.017.017 0 00.006.004l.007.001h10.964l.007-.001a.016.016 0 00.006-.004.016.016 0 00.004-.006l.001-.007a.017.017 0 00-.003-.01l-1.703-2.554a1.75 1.75 0 01-.294-.97V5A3.5 3.5 0 008 1.5zM3 5a5 5 0 0110 0v2.947c0 .05.015.098.042.139l1.703 2.555A1.518 1.518 0 0113.482 13H2.518a1.518 1.518 0 01-1.263-2.36l1.703-2.554A.25.25 0 003 7.947V5z"></path></svg>
      </a>
    </notification-indicator>

  </div>


  <div class="Header-item position-relative d-none d-md-flex">
    <details class="details-overlay details-reset">
  <summary class="Header-link"
      aria-label="Create new…"
      data-ga-click="Header, create new, icon:add">
    <svg class="octicon octicon-plus" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M8 2a.75.75 0 01.75.75v4.5h4.5a.75.75 0 010 1.5h-4.5v4.5a.75.75 0 01-1.5 0v-4.5h-4.5a.75.75 0 010-1.5h4.5v-4.5A.75.75 0 018 2z"></path></svg> <span class="dropdown-caret"></span>
  </summary>
  <details-menu class="dropdown-menu dropdown-menu-sw mt-n2">
    
<a role="menuitem" class="dropdown-item" href="/new" data-ga-click="Header, create new repository">
  New repository
</a>

  <a role="menuitem" class="dropdown-item" href="/new/import" data-ga-click="Header, import a repository">
    Import repository
  </a>

<a role="menuitem" class="dropdown-item" href="https://gist.github.com/" data-ga-click="Header, create new gist">
  New gist
</a>

  <a role="menuitem" class="dropdown-item" href="/organizations/new" data-ga-click="Header, create new organization">
    New organization
  </a>


  <div role="none" class="dropdown-divider"></div>
  <div class="dropdown-header">
    <span title="goat-community/goat">This repository</span>
  </div>
    <a role="menuitem" class="dropdown-item" href="/goat-community/goat/issues/new/choose" data-ga-click="Header, create new issue" data-skip-pjax>
      New issue
    </a>


  </details-menu>
</details>

  </div>

  <div class="Header-item position-relative mr-0 d-none d-md-flex">
    
  <details class="details-overlay details-reset js-feature-preview-indicator-container" data-feature-preview-indicator-src="/users/rafleo2008/feature_preview/indicator_check">

  <summary class="Header-link"
    aria-label="View profile and more"
    data-ga-click="Header, show menu, icon:avatar">
    <img
  alt="@rafleo2008"
  width="20"
  height="20"
  src="https://avatars1.githubusercontent.com/u/58067217?s=60&amp;v=4"
  class="avatar avatar-user " />

      <span class="feature-preview-indicator js-feature-preview-indicator" style="top: 10px;" hidden></span>
    <span class="dropdown-caret"></span>
  </summary>
  <details-menu class="dropdown-menu dropdown-menu-sw mt-n2" style="width: 180px" >
    <div class="header-nav-current-user css-truncate"><a role="menuitem" class="no-underline user-profile-link px-3 pt-2 pb-2 mb-n2 mt-n1 d-block" href="/rafleo2008" data-ga-click="Header, go to profile, text:Signed in as">Signed in as <strong class="css-truncate-target">rafleo2008</strong></a></div>
    <div role="none" class="dropdown-divider"></div>

      <div class="pl-3 pr-3 f6 user-status-container js-user-status-context lh-condensed" data-url="/users/status?compact=1&amp;link_mentions=0&amp;truncate=1">
        
<div class="js-user-status-container rounded-1 px-2 py-1 mt-2 border"
  data-team-hovercards-enabled>
  <details class="js-user-status-details details-reset details-overlay details-overlay-dark">
    <summary class="btn-link btn-block link-gray no-underline js-toggle-user-status-edit toggle-user-status-edit "
      role="menuitem" data-hydro-click="{&quot;event_type&quot;:&quot;user_profile.click&quot;,&quot;payload&quot;:{&quot;profile_user_id&quot;:58163984,&quot;target&quot;:&quot;EDIT_USER_STATUS&quot;,&quot;user_id&quot;:58067217,&quot;originating_url&quot;:&quot;https://github.com/goat-community/goat/blob/main/app/database/data_preparation/SQL/pois.sql&quot;}}" data-hydro-click-hmac="09268df0c1ccacf940d0965d31b5e2f8140389012ec2961f2589b8b478dcb741">
      <div class="d-flex flex-items-center flex-items-stretch">
        <div class="f6 lh-condensed user-status-header d-flex user-status-emoji-only-header circle">
          <div class="user-status-emoji-container flex-shrink-0 mr-2 d-flex flex-items-center flex-justify-center lh-condensed-ultra v-align-bottom">
            <svg class="octicon octicon-smiley" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M1.5 8a6.5 6.5 0 1113 0 6.5 6.5 0 01-13 0zM8 0a8 8 0 100 16A8 8 0 008 0zM5 8a1 1 0 100-2 1 1 0 000 2zm7-1a1 1 0 11-2 0 1 1 0 012 0zM5.32 9.636a.75.75 0 011.038.175l.007.009c.103.118.22.222.35.31.264.178.683.37 1.285.37.602 0 1.02-.192 1.285-.371.13-.088.247-.192.35-.31l.007-.008a.75.75 0 111.222.87l-.614-.431c.614.43.614.431.613.431v.001l-.001.002-.002.003-.005.007-.014.019a1.984 1.984 0 01-.184.213c-.16.166-.338.316-.53.445-.63.418-1.37.638-2.127.629-.946 0-1.652-.308-2.126-.63a3.32 3.32 0 01-.715-.657l-.014-.02-.005-.006-.002-.003v-.002h-.001l.613-.432-.614.43a.75.75 0 01.183-1.044h.001z"></path></svg>
          </div>
        </div>
        <div class="
          
           user-status-message-wrapper f6 min-width-0"
           style="line-height: 20px;" >
          <div class="css-truncate css-truncate-target width-fit text-gray-dark text-left">
              <span class="text-gray">Set status</span>
          </div>
        </div>
      </div>
    </summary>
    <details-dialog class="details-dialog rounded-1 anim-fade-in fast Box Box--overlay" role="dialog" tabindex="-1">
      <!-- '"` --><!-- </textarea></xmp> --></option></form><form class="position-relative flex-auto js-user-status-form" action="/users/status?circle=0&amp;compact=1&amp;link_mentions=0&amp;truncate=1" accept-charset="UTF-8" method="post"><input type="hidden" name="_method" value="put" /><input type="hidden" name="authenticity_token" value="1BFwBHIuHohzVWrUq+uy2BGWyCo/RPzLWkMVQOizxyhSH2jxbCWx7iz/6hxR+ZWv4fkTjatDhS3CghI04+jbbg==" />
        <div class="Box-header bg-gray border-bottom p-3">
          <button class="Box-btn-octicon js-toggle-user-status-edit btn-octicon float-right" type="reset" aria-label="Close dialog" data-close-dialog>
            <svg class="octicon octicon-x" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M3.72 3.72a.75.75 0 011.06 0L8 6.94l3.22-3.22a.75.75 0 111.06 1.06L9.06 8l3.22 3.22a.75.75 0 11-1.06 1.06L8 9.06l-3.22 3.22a.75.75 0 01-1.06-1.06L6.94 8 3.72 4.78a.75.75 0 010-1.06z"></path></svg>
          </button>
          <h3 class="Box-title f5 text-bold text-gray-dark">Edit status</h3>
        </div>
        <input type="hidden" name="emoji" class="js-user-status-emoji-field" value="">
        <input type="hidden" name="organization_id" class="js-user-status-org-id-field" value="">
        <div class="px-3 py-2 text-gray-dark">
          <div class="js-characters-remaining-container position-relative mt-2">
            <div class="input-group d-table form-group my-0 js-user-status-form-group">
              <span class="input-group-button d-table-cell v-align-middle" style="width: 1%">
                <button type="button" aria-label="Choose an emoji" class="btn-outline btn js-toggle-user-status-emoji-picker btn-open-emoji-picker p-0">
                  <span class="js-user-status-original-emoji" hidden></span>
                  <span class="js-user-status-custom-emoji"></span>
                  <span class="js-user-status-no-emoji-icon" >
                    <svg class="octicon octicon-smiley" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M1.5 8a6.5 6.5 0 1113 0 6.5 6.5 0 01-13 0zM8 0a8 8 0 100 16A8 8 0 008 0zM5 8a1 1 0 100-2 1 1 0 000 2zm7-1a1 1 0 11-2 0 1 1 0 012 0zM5.32 9.636a.75.75 0 011.038.175l.007.009c.103.118.22.222.35.31.264.178.683.37 1.285.37.602 0 1.02-.192 1.285-.371.13-.088.247-.192.35-.31l.007-.008a.75.75 0 111.222.87l-.614-.431c.614.43.614.431.613.431v.001l-.001.002-.002.003-.005.007-.014.019a1.984 1.984 0 01-.184.213c-.16.166-.338.316-.53.445-.63.418-1.37.638-2.127.629-.946 0-1.652-.308-2.126-.63a3.32 3.32 0 01-.715-.657l-.014-.02-.005-.006-.002-.003v-.002h-.001l.613-.432-.614.43a.75.75 0 01.183-1.044h.001z"></path></svg>
                  </span>
                </button>
              </span>
              <text-expander keys=": @" data-mention-url="/autocomplete/user-suggestions" data-emoji-url="/autocomplete/emoji">
                <input
                  type="text"
                  autocomplete="off"
                  data-no-org-url="/autocomplete/user-suggestions"
                  data-org-url="/suggestions?mention_suggester=1"
                  data-maxlength="80"
                  class="d-table-cell width-full form-control js-user-status-message-field js-characters-remaining-field"
                  placeholder="What's happening?"
                  name="message"
                  value=""
                  aria-label="What is your current status?">
              </text-expander>
              <div class="error">Could not update your status, please try again.</div>
            </div>
            <div style="margin-left: 53px" class="my-1 text-small label-characters-remaining js-characters-remaining" data-suffix="remaining" hidden>
              80 remaining
            </div>
          </div>
          <include-fragment class="js-user-status-emoji-picker" data-url="/users/status/emoji"></include-fragment>
          <div class="overflow-auto ml-n3 mr-n3 px-3 border-bottom" style="max-height: 33vh">
            <div class="user-status-suggestions js-user-status-suggestions collapsed overflow-hidden">
              <h4 class="f6 text-normal my-3">Suggestions:</h4>
              <div class="mx-3 mt-2 clearfix">
                  <div class="float-left col-6">
                      <button type="button" value=":palm_tree:" class="d-flex flex-items-baseline flex-items-stretch lh-condensed f6 btn-link link-gray no-underline js-predefined-user-status mb-1">
                        <div class="emoji-status-width mr-2 v-align-middle js-predefined-user-status-emoji">
                          <g-emoji alias="palm_tree" fallback-src="https://github.githubassets.com/images/icons/emoji/unicode/1f334.png">🌴</g-emoji>
                        </div>
                        <div class="d-flex flex-items-center no-underline js-predefined-user-status-message ws-normal text-left" style="border-left: 1px solid transparent">
                          On vacation
                        </div>
                      </button>
                      <button type="button" value=":face_with_thermometer:" class="d-flex flex-items-baseline flex-items-stretch lh-condensed f6 btn-link link-gray no-underline js-predefined-user-status mb-1">
                        <div class="emoji-status-width mr-2 v-align-middle js-predefined-user-status-emoji">
                          <g-emoji alias="face_with_thermometer" fallback-src="https://github.githubassets.com/images/icons/emoji/unicode/1f912.png">🤒</g-emoji>
                        </div>
                        <div class="d-flex flex-items-center no-underline js-predefined-user-status-message ws-normal text-left" style="border-left: 1px solid transparent">
                          Out sick
                        </div>
                      </button>
                  </div>
                  <div class="float-left col-6">
                      <button type="button" value=":house:" class="d-flex flex-items-baseline flex-items-stretch lh-condensed f6 btn-link link-gray no-underline js-predefined-user-status mb-1">
                        <div class="emoji-status-width mr-2 v-align-middle js-predefined-user-status-emoji">
                          <g-emoji alias="house" fallback-src="https://github.githubassets.com/images/icons/emoji/unicode/1f3e0.png">🏠</g-emoji>
                        </div>
                        <div class="d-flex flex-items-center no-underline js-predefined-user-status-message ws-normal text-left" style="border-left: 1px solid transparent">
                          Working from home
                        </div>
                      </button>
                      <button type="button" value=":dart:" class="d-flex flex-items-baseline flex-items-stretch lh-condensed f6 btn-link link-gray no-underline js-predefined-user-status mb-1">
                        <div class="emoji-status-width mr-2 v-align-middle js-predefined-user-status-emoji">
                          <g-emoji alias="dart" fallback-src="https://github.githubassets.com/images/icons/emoji/unicode/1f3af.png">🎯</g-emoji>
                        </div>
                        <div class="d-flex flex-items-center no-underline js-predefined-user-status-message ws-normal text-left" style="border-left: 1px solid transparent">
                          Focusing
                        </div>
                      </button>
                  </div>
              </div>
            </div>
            <div class="user-status-limited-availability-container">
              <div class="form-checkbox my-0">
                <input type="checkbox" name="limited_availability" value="1" class="js-user-status-limited-availability-checkbox" data-default-message="I may be slow to respond." aria-describedby="limited-availability-help-text-truncate-true-compact-true" id="limited-availability-truncate-true-compact-true">
                <label class="d-block f5 text-gray-dark mb-1" for="limited-availability-truncate-true-compact-true">
                  Busy
                </label>
                <p class="note" id="limited-availability-help-text-truncate-true-compact-true">
                  When others mention you, assign you, or request your review,
                  GitHub will let them know that you have limited availability.
                </p>
              </div>
            </div>
          </div>
          <div class="d-inline-block f5 mr-2 pt-3 pb-2" >
  <div class="d-inline-block mr-1">
    Clear status
  </div>

  <details class="js-user-status-expire-drop-down f6 dropdown details-reset details-overlay d-inline-block mr-2">
    <summary class="btn btn-sm v-align-baseline" aria-haspopup="true">
      <div class="js-user-status-expiration-interval-selected d-inline-block v-align-baseline">
        Never
      </div>
      <div class="dropdown-caret"></div>
    </summary>

    <ul class="dropdown-menu dropdown-menu-se pl-0 overflow-auto" style="width: 220px; max-height: 15.5em">
      <li>
        <button type="button" class="btn-link dropdown-item js-user-status-expire-button ws-normal" title="Never">
          <span class="d-inline-block text-bold mb-1">Never</span>
          <div class="f6 lh-condensed">Keep this status until you clear your status or edit your status.</div>
        </button>
      </li>
      <li class="dropdown-divider" role="none"></li>
        <li>
          <button type="button" class="btn-link dropdown-item ws-normal js-user-status-expire-button" title="in 30 minutes" value="2020-08-30T16:24:23+02:00">
            in 30 minutes
          </button>
        </li>
        <li>
          <button type="button" class="btn-link dropdown-item ws-normal js-user-status-expire-button" title="in 1 hour" value="2020-08-30T16:54:23+02:00">
            in 1 hour
          </button>
        </li>
        <li>
          <button type="button" class="btn-link dropdown-item ws-normal js-user-status-expire-button" title="in 4 hours" value="2020-08-30T19:54:23+02:00">
            in 4 hours
          </button>
        </li>
        <li>
          <button type="button" class="btn-link dropdown-item ws-normal js-user-status-expire-button" title="today" value="2020-08-30T23:59:59+02:00">
            today
          </button>
        </li>
        <li>
          <button type="button" class="btn-link dropdown-item ws-normal js-user-status-expire-button" title="this week" value="2020-08-30T23:59:59+02:00">
            this week
          </button>
        </li>
    </ul>
  </details>
  <input class="js-user-status-expiration-date-input" type="hidden" name="expires_at" value="">
</div>

          <include-fragment class="js-user-status-org-picker" data-url="/users/status/organizations"></include-fragment>
        </div>
        <div class="d-flex flex-items-center flex-justify-between p-3 border-top">
          <button type="submit" disabled class="width-full btn btn-primary mr-2 js-user-status-submit">
            Set status
          </button>
          <button type="button" disabled class="width-full js-clear-user-status-button btn ml-2 ">
            Clear status
          </button>
        </div>
</form>    </details-dialog>
  </details>
</div>

      </div>
      <div role="none" class="dropdown-divider"></div>

    <a role="menuitem" class="dropdown-item" href="/rafleo2008" data-ga-click="Header, go to profile, text:your profile" data-hydro-click="{&quot;event_type&quot;:&quot;global_header.user_menu_dropdown.click&quot;,&quot;payload&quot;:{&quot;request_url&quot;:&quot;https://github.com/goat-community/goat/blob/main/app/database/data_preparation/SQL/pois.sql&quot;,&quot;target&quot;:&quot;YOUR_PROFILE&quot;,&quot;originating_url&quot;:&quot;https://github.com/goat-community/goat/blob/main/app/database/data_preparation/SQL/pois.sql&quot;,&quot;user_id&quot;:58067217}}" data-hydro-click-hmac="c4483980af0dce7e966fbb8de78e083100f18ce317cba76c8b32548251bb2913" >Your profile</a>

    <a role="menuitem" class="dropdown-item" href="/rafleo2008?tab=repositories" data-ga-click="Header, go to repositories, text:your repositories" data-hydro-click="{&quot;event_type&quot;:&quot;global_header.user_menu_dropdown.click&quot;,&quot;payload&quot;:{&quot;request_url&quot;:&quot;https://github.com/goat-community/goat/blob/main/app/database/data_preparation/SQL/pois.sql&quot;,&quot;target&quot;:&quot;YOUR_REPOSITORIES&quot;,&quot;originating_url&quot;:&quot;https://github.com/goat-community/goat/blob/main/app/database/data_preparation/SQL/pois.sql&quot;,&quot;user_id&quot;:58067217}}" data-hydro-click-hmac="d891904783de4091ba795c67fc9330136cdc18ac6c3f9e6a148931bc02ba326a" >Your repositories</a>



    <a role="menuitem" class="dropdown-item" href="/rafleo2008?tab=projects" data-ga-click="Header, go to projects, text:your projects" data-hydro-click="{&quot;event_type&quot;:&quot;global_header.user_menu_dropdown.click&quot;,&quot;payload&quot;:{&quot;request_url&quot;:&quot;https://github.com/goat-community/goat/blob/main/app/database/data_preparation/SQL/pois.sql&quot;,&quot;target&quot;:&quot;YOUR_PROJECTS&quot;,&quot;originating_url&quot;:&quot;https://github.com/goat-community/goat/blob/main/app/database/data_preparation/SQL/pois.sql&quot;,&quot;user_id&quot;:58067217}}" data-hydro-click-hmac="15762db7d3547b012260ec28a789be20acd3ba8c0c1db057c5ea533b47326461" >Your projects</a>


    <a role="menuitem" class="dropdown-item" href="/rafleo2008?tab=stars" data-ga-click="Header, go to starred repos, text:your stars" data-hydro-click="{&quot;event_type&quot;:&quot;global_header.user_menu_dropdown.click&quot;,&quot;payload&quot;:{&quot;request_url&quot;:&quot;https://github.com/goat-community/goat/blob/main/app/database/data_preparation/SQL/pois.sql&quot;,&quot;target&quot;:&quot;YOUR_STARS&quot;,&quot;originating_url&quot;:&quot;https://github.com/goat-community/goat/blob/main/app/database/data_preparation/SQL/pois.sql&quot;,&quot;user_id&quot;:58067217}}" data-hydro-click-hmac="9e186213f6ca8d1f4f920e6769dfe98b526c63cd477e37d9fe1d7b7a2cf7658d" >Your stars</a>
      <a role="menuitem" class="dropdown-item" href="https://gist.github.com/mine" data-ga-click="Header, your gists, text:your gists" data-hydro-click="{&quot;event_type&quot;:&quot;global_header.user_menu_dropdown.click&quot;,&quot;payload&quot;:{&quot;request_url&quot;:&quot;https://github.com/goat-community/goat/blob/main/app/database/data_preparation/SQL/pois.sql&quot;,&quot;target&quot;:&quot;YOUR_GISTS&quot;,&quot;originating_url&quot;:&quot;https://github.com/goat-community/goat/blob/main/app/database/data_preparation/SQL/pois.sql&quot;,&quot;user_id&quot;:58067217}}" data-hydro-click-hmac="bea82f1b05b731d51c82b93c9dd7fbbe55784d6d4f73d9eb429573a30af92622" >Your gists</a>





    <div role="none" class="dropdown-divider"></div>
      <a role="menuitem" class="dropdown-item" href="/settings/billing" data-ga-click="Header, go to billing, text:upgrade" data-hydro-click="{&quot;event_type&quot;:&quot;global_header.user_menu_dropdown.click&quot;,&quot;payload&quot;:{&quot;request_url&quot;:&quot;https://github.com/goat-community/goat/blob/main/app/database/data_preparation/SQL/pois.sql&quot;,&quot;target&quot;:&quot;UPGRADE&quot;,&quot;originating_url&quot;:&quot;https://github.com/goat-community/goat/blob/main/app/database/data_preparation/SQL/pois.sql&quot;,&quot;user_id&quot;:58067217}}" data-hydro-click-hmac="6e04bfc9d9408e26602bde49962ff1579e1718e20916710452d6bceac31fa05b" >Upgrade</a>
      
<div id="feature-enrollment-toggle" class="hide-sm hide-md feature-preview-details position-relative">
  <button
    type="button"
    class="dropdown-item btn-link"
    role="menuitem"
    data-feature-preview-trigger-url="/users/rafleo2008/feature_previews"
    data-feature-preview-close-details="{&quot;event_type&quot;:&quot;feature_preview.clicks.close_modal&quot;,&quot;payload&quot;:{&quot;originating_url&quot;:&quot;https://github.com/goat-community/goat/blob/main/app/database/data_preparation/SQL/pois.sql&quot;,&quot;user_id&quot;:58067217}}"
    data-feature-preview-close-hmac="251ae3bbed13c699905149086377b41b65aa7b508e99f4a65aadccb7ee439a04"
    data-hydro-click="{&quot;event_type&quot;:&quot;feature_preview.clicks.open_modal&quot;,&quot;payload&quot;:{&quot;link_location&quot;:&quot;user_dropdown&quot;,&quot;originating_url&quot;:&quot;https://github.com/goat-community/goat/blob/main/app/database/data_preparation/SQL/pois.sql&quot;,&quot;user_id&quot;:58067217}}"
    data-hydro-click-hmac="64e5baecb135a6896fc1d692fa2562f73b2042a5d3a4f871a715efecf8e385e3"
  >
    Feature preview
  </button>
    <span class="feature-preview-indicator js-feature-preview-indicator" hidden></span>
</div>

    <a role="menuitem" class="dropdown-item" href="https://docs.github.com" data-ga-click="Header, go to help, text:help" data-hydro-click="{&quot;event_type&quot;:&quot;global_header.user_menu_dropdown.click&quot;,&quot;payload&quot;:{&quot;request_url&quot;:&quot;https://github.com/goat-community/goat/blob/main/app/database/data_preparation/SQL/pois.sql&quot;,&quot;target&quot;:&quot;HELP&quot;,&quot;originating_url&quot;:&quot;https://github.com/goat-community/goat/blob/main/app/database/data_preparation/SQL/pois.sql&quot;,&quot;user_id&quot;:58067217}}" data-hydro-click-hmac="b5ec4c9e8ed4f94dc1efecdaffbd8d5985060118e22742493f302183567a73b8" >Help</a>
    <a role="menuitem" class="dropdown-item" href="/settings/profile" data-ga-click="Header, go to settings, icon:settings" data-hydro-click="{&quot;event_type&quot;:&quot;global_header.user_menu_dropdown.click&quot;,&quot;payload&quot;:{&quot;request_url&quot;:&quot;https://github.com/goat-community/goat/blob/main/app/database/data_preparation/SQL/pois.sql&quot;,&quot;target&quot;:&quot;SETTINGS&quot;,&quot;originating_url&quot;:&quot;https://github.com/goat-community/goat/blob/main/app/database/data_preparation/SQL/pois.sql&quot;,&quot;user_id&quot;:58067217}}" data-hydro-click-hmac="60c3ebab0cd04707f68c539efc49fcf320c4c5ed9ebf12773d19d419c323e862" >Settings</a>
    <!-- '"` --><!-- </textarea></xmp> --></option></form><form class="logout-form" action="/logout" accept-charset="UTF-8" method="post"><input type="hidden" name="authenticity_token" value="4BJCbLOdGfHYpAXnudXPbh2a0hcVvxZWVvd1G6DZQeU4zeCBGxB2Q0YVp9f0smXs/aXm5nSt9kHAy5zas7+jVQ==" />
      
      <button type="submit" class="dropdown-item dropdown-signout" data-ga-click="Header, sign out, icon:logout" data-hydro-click="{&quot;event_type&quot;:&quot;global_header.user_menu_dropdown.click&quot;,&quot;payload&quot;:{&quot;request_url&quot;:&quot;https://github.com/goat-community/goat/blob/main/app/database/data_preparation/SQL/pois.sql&quot;,&quot;target&quot;:&quot;SIGN_OUT&quot;,&quot;originating_url&quot;:&quot;https://github.com/goat-community/goat/blob/main/app/database/data_preparation/SQL/pois.sql&quot;,&quot;user_id&quot;:58067217}}" data-hydro-click-hmac="2e61a2a05c3f673a86e9fb2cdde58300f537f38c43c88ccd0e8a5344376972a8"  role="menuitem">
        Sign out
      </button>
      <input type="text" name="required_field_81d8" hidden="hidden" class="form-control" /><input type="hidden" name="timestamp" value="1598795663874" class="form-control" /><input type="hidden" name="timestamp_secret" value="2fcd18f5a1cfeef62bb1724f80d96c2470c921c49a8bc3e8de7750ad6a5791fd" class="form-control" />
</form>  </details-menu>
</details>

  </div>

</header>

          

    </div>

  <div id="start-of-content" class="show-on-focus"></div>




    <div id="js-flash-container">


  <template class="js-flash-template">
    <div class="flash flash-full  {{ className }}">
  <div class=" px-2" >
    <button class="flash-close js-flash-close" type="button" aria-label="Dismiss this message">
      <svg class="octicon octicon-x" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M3.72 3.72a.75.75 0 011.06 0L8 6.94l3.22-3.22a.75.75 0 111.06 1.06L9.06 8l3.22 3.22a.75.75 0 11-1.06 1.06L8 9.06l-3.22 3.22a.75.75 0 01-1.06-1.06L6.94 8 3.72 4.78a.75.75 0 010-1.06z"></path></svg>
    </button>
    
      <div>{{ message }}</div>

  </div>
</div>
  </template>
</div>


  

  <include-fragment class="js-notification-shelf-include-fragment" data-base-src="https://github.com/notifications/beta/shelf"></include-fragment>



  <div
    class="application-main "
    data-commit-hovercards-enabled
    data-discussion-hovercards-enabled
    data-issue-and-pr-hovercards-enabled
  >
        <div itemscope itemtype="http://schema.org/SoftwareSourceCode" class="">
    <main  >
      

  


  










  <div class="bg-gray-light pt-3 hide-full-screen mb-5">

    <div class="d-flex mb-3 px-3 px-md-4 px-lg-5">

      <div class="flex-auto min-width-0 width-fit mr-3">
        <h1 class=" d-flex flex-wrap flex-items-center break-word f3 text-normal">
    <svg class="octicon octicon-repo text-gray" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9zm10.5-1V9h-8c-.356 0-.694.074-1 .208V2.5a1 1 0 011-1h8zM5 12.25v3.25a.25.25 0 00.4.2l1.45-1.087a.25.25 0 01.3 0L8.6 15.7a.25.25 0 00.4-.2v-3.25a.25.25 0 00-.25-.25h-3.5a.25.25 0 00-.25.25z"></path></svg>
  <span class="author ml-2 flex-self-stretch" itemprop="author">
    <a class="url fn" rel="author" data-hovercard-type="organization" data-hovercard-url="/orgs/goat-community/hovercard" href="/goat-community">goat-community</a>
  </span>
  <span class="mx-1 flex-self-stretch">/</span>
  <strong itemprop="name" class="mr-2 flex-self-stretch">
    <a data-pjax="#js-repo-pjax-container" href="/goat-community/goat">goat</a>
  </strong>
  
</h1>


      </div>

      <ul class="pagehead-actions flex-shrink-0 d-none d-md-inline" style="padding: 2px 0;">

  <li>
        <form data-remote="true" class="d-flex js-social-form js-social-container" action="/notifications/subscribe" accept-charset="UTF-8" method="post"><input type="hidden" name="authenticity_token" value="42jjAv5O4HqyEn5Gf1NfqfCchpk1nt9wBse+aOLgfuongPQasAikrgwOkwa/21cXCBDG1bgIvpIMPQY5+YDV+A==" />      <input type="hidden" name="repository_id" value="150960118">

      <details class="details-reset details-overlay select-menu hx_rsm">
        <summary class="btn btn-sm btn-with-count" data-hydro-click="{&quot;event_type&quot;:&quot;repository.click&quot;,&quot;payload&quot;:{&quot;target&quot;:&quot;WATCH_BUTTON&quot;,&quot;repository_id&quot;:150960118,&quot;originating_url&quot;:&quot;https://github.com/goat-community/goat/blob/main/app/database/data_preparation/SQL/pois.sql&quot;,&quot;user_id&quot;:58067217}}" data-hydro-click-hmac="5acd67301858877c25d7a076c08f11b8e553b4ac7d6e05afa6c73cc0c8fa5f3c" data-ga-click="Repository, click Watch settings, action:blob#show">          <span data-menu-button>
              <svg height="16" class="octicon octicon-eye" viewBox="0 0 16 16" version="1.1" width="16" aria-hidden="true"><path fill-rule="evenodd" d="M1.679 7.932c.412-.621 1.242-1.75 2.366-2.717C5.175 4.242 6.527 3.5 8 3.5c1.473 0 2.824.742 3.955 1.715 1.124.967 1.954 2.096 2.366 2.717a.119.119 0 010 .136c-.412.621-1.242 1.75-2.366 2.717C10.825 11.758 9.473 12.5 8 12.5c-1.473 0-2.824-.742-3.955-1.715C2.92 9.818 2.09 8.69 1.679 8.068a.119.119 0 010-.136zM8 2c-1.981 0-3.67.992-4.933 2.078C1.797 5.169.88 6.423.43 7.1a1.619 1.619 0 000 1.798c.45.678 1.367 1.932 2.637 3.024C4.329 13.008 6.019 14 8 14c1.981 0 3.67-.992 4.933-2.078 1.27-1.091 2.187-2.345 2.637-3.023a1.619 1.619 0 000-1.798c-.45-.678-1.367-1.932-2.637-3.023C11.671 2.992 9.981 2 8 2zm0 8a2 2 0 100-4 2 2 0 000 4z"></path></svg>
              Watch
          </span>
          <span class="dropdown-caret"></span>
</summary>        <details-menu
          class="select-menu-modal position-absolute mt-5"
          style="z-index: 99;">
          <div class="select-menu-header">
            <span class="select-menu-title">Notifications</span>
          </div>
          <div class="select-menu-list">
            <button type="submit" name="do" value="included" class="select-menu-item width-full" aria-checked="true" role="menuitemradio">
              <svg class="octicon octicon-check select-menu-item-icon" height="16" viewBox="0 0 16 16" version="1.1" width="16" aria-hidden="true"><path fill-rule="evenodd" d="M13.78 4.22a.75.75 0 010 1.06l-7.25 7.25a.75.75 0 01-1.06 0L2.22 9.28a.75.75 0 011.06-1.06L6 10.94l6.72-6.72a.75.75 0 011.06 0z"></path></svg>
              <div class="select-menu-item-text">
                <span class="select-menu-item-heading">Not watching</span>
                <span class="description">Be notified only when participating or @mentioned.</span>
                <span class="hidden-select-button-text" data-menu-button-contents>
                  <svg height="16" class="octicon octicon-eye" viewBox="0 0 16 16" version="1.1" width="16" aria-hidden="true"><path fill-rule="evenodd" d="M1.679 7.932c.412-.621 1.242-1.75 2.366-2.717C5.175 4.242 6.527 3.5 8 3.5c1.473 0 2.824.742 3.955 1.715 1.124.967 1.954 2.096 2.366 2.717a.119.119 0 010 .136c-.412.621-1.242 1.75-2.366 2.717C10.825 11.758 9.473 12.5 8 12.5c-1.473 0-2.824-.742-3.955-1.715C2.92 9.818 2.09 8.69 1.679 8.068a.119.119 0 010-.136zM8 2c-1.981 0-3.67.992-4.933 2.078C1.797 5.169.88 6.423.43 7.1a1.619 1.619 0 000 1.798c.45.678 1.367 1.932 2.637 3.024C4.329 13.008 6.019 14 8 14c1.981 0 3.67-.992 4.933-2.078 1.27-1.091 2.187-2.345 2.637-3.023a1.619 1.619 0 000-1.798c-.45-.678-1.367-1.932-2.637-3.023C11.671 2.992 9.981 2 8 2zm0 8a2 2 0 100-4 2 2 0 000 4z"></path></svg>
                  Watch
                </span>
              </div>
            </button>

            <button type="submit" name="do" value="release_only" class="select-menu-item width-full" aria-checked="false" role="menuitemradio">
              <svg class="octicon octicon-check select-menu-item-icon" height="16" viewBox="0 0 16 16" version="1.1" width="16" aria-hidden="true"><path fill-rule="evenodd" d="M13.78 4.22a.75.75 0 010 1.06l-7.25 7.25a.75.75 0 01-1.06 0L2.22 9.28a.75.75 0 011.06-1.06L6 10.94l6.72-6.72a.75.75 0 011.06 0z"></path></svg>
              <div class="select-menu-item-text">
                <span class="select-menu-item-heading">Releases only</span>
                <span class="description">Be notified of new releases, and when participating or @mentioned.</span>
                <span class="hidden-select-button-text" data-menu-button-contents>
                  <svg height="16" class="octicon octicon-eye" viewBox="0 0 16 16" version="1.1" width="16" aria-hidden="true"><path fill-rule="evenodd" d="M1.679 7.932c.412-.621 1.242-1.75 2.366-2.717C5.175 4.242 6.527 3.5 8 3.5c1.473 0 2.824.742 3.955 1.715 1.124.967 1.954 2.096 2.366 2.717a.119.119 0 010 .136c-.412.621-1.242 1.75-2.366 2.717C10.825 11.758 9.473 12.5 8 12.5c-1.473 0-2.824-.742-3.955-1.715C2.92 9.818 2.09 8.69 1.679 8.068a.119.119 0 010-.136zM8 2c-1.981 0-3.67.992-4.933 2.078C1.797 5.169.88 6.423.43 7.1a1.619 1.619 0 000 1.798c.45.678 1.367 1.932 2.637 3.024C4.329 13.008 6.019 14 8 14c1.981 0 3.67-.992 4.933-2.078 1.27-1.091 2.187-2.345 2.637-3.023a1.619 1.619 0 000-1.798c-.45-.678-1.367-1.932-2.637-3.023C11.671 2.992 9.981 2 8 2zm0 8a2 2 0 100-4 2 2 0 000 4z"></path></svg>
                  Unwatch releases
                </span>
              </div>
            </button>

            <button type="submit" name="do" value="subscribed" class="select-menu-item width-full" aria-checked="false" role="menuitemradio">
              <svg class="octicon octicon-check select-menu-item-icon" height="16" viewBox="0 0 16 16" version="1.1" width="16" aria-hidden="true"><path fill-rule="evenodd" d="M13.78 4.22a.75.75 0 010 1.06l-7.25 7.25a.75.75 0 01-1.06 0L2.22 9.28a.75.75 0 011.06-1.06L6 10.94l6.72-6.72a.75.75 0 011.06 0z"></path></svg>
              <div class="select-menu-item-text">
                <span class="select-menu-item-heading">Watching</span>
                <span class="description">Be notified of all conversations.</span>
                <span class="hidden-select-button-text" data-menu-button-contents>
                  <svg class="octicon octicon-eye v-align-text-bottom" height="16" viewBox="0 0 16 16" version="1.1" width="16" aria-hidden="true"><path fill-rule="evenodd" d="M1.679 7.932c.412-.621 1.242-1.75 2.366-2.717C5.175 4.242 6.527 3.5 8 3.5c1.473 0 2.824.742 3.955 1.715 1.124.967 1.954 2.096 2.366 2.717a.119.119 0 010 .136c-.412.621-1.242 1.75-2.366 2.717C10.825 11.758 9.473 12.5 8 12.5c-1.473 0-2.824-.742-3.955-1.715C2.92 9.818 2.09 8.69 1.679 8.068a.119.119 0 010-.136zM8 2c-1.981 0-3.67.992-4.933 2.078C1.797 5.169.88 6.423.43 7.1a1.619 1.619 0 000 1.798c.45.678 1.367 1.932 2.637 3.024C4.329 13.008 6.019 14 8 14c1.981 0 3.67-.992 4.933-2.078 1.27-1.091 2.187-2.345 2.637-3.023a1.619 1.619 0 000-1.798c-.45-.678-1.367-1.932-2.637-3.023C11.671 2.992 9.981 2 8 2zm0 8a2 2 0 100-4 2 2 0 000 4z"></path></svg>
                  Unwatch
                </span>
              </div>
            </button>

            <button type="submit" name="do" value="ignore" class="select-menu-item width-full" aria-checked="false" role="menuitemradio">
              <svg class="octicon octicon-check select-menu-item-icon" height="16" viewBox="0 0 16 16" version="1.1" width="16" aria-hidden="true"><path fill-rule="evenodd" d="M13.78 4.22a.75.75 0 010 1.06l-7.25 7.25a.75.75 0 01-1.06 0L2.22 9.28a.75.75 0 011.06-1.06L6 10.94l6.72-6.72a.75.75 0 011.06 0z"></path></svg>
              <div class="select-menu-item-text">
                <span class="select-menu-item-heading">Ignoring</span>
                <span class="description">Never be notified.</span>
                <span class="hidden-select-button-text" data-menu-button-contents>
                  <svg height="16" class="octicon octicon-bell-slash" viewBox="0 0 16 16" version="1.1" width="16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5c-.997 0-1.895.416-2.534 1.086A.75.75 0 014.38 1.55 5 5 0 0113 5v2.373a.75.75 0 01-1.5 0V5A3.5 3.5 0 008 1.5zM4.182 4.31L1.19 2.143a.75.75 0 10-.88 1.214L3 5.305v2.642a.25.25 0 01-.042.139L1.255 10.64A1.518 1.518 0 002.518 13h11.108l1.184.857a.75.75 0 10.88-1.214l-1.375-.996a1.196 1.196 0 00-.013-.01L4.198 4.321a.733.733 0 00-.016-.011zm7.373 7.19L4.5 6.391v1.556c0 .346-.102.683-.294.97l-1.703 2.556a.018.018 0 00-.003.01.015.015 0 00.005.012.017.017 0 00.006.004l.007.001h9.037zM8 16a2 2 0 001.985-1.75c.017-.137-.097-.25-.235-.25h-3.5c-.138 0-.252.113-.235.25A2 2 0 008 16z"></path></svg>
                  Stop ignoring
                </span>
              </div>
            </button>
          </div>
        </details-menu>
      </details>
        <a class="social-count js-social-count"
          href="/goat-community/goat/watchers"
          aria-label="4 users are watching this repository">
          4
        </a>
</form>
  </li>

  <li>
      <div class="js-toggler-container js-social-container starring-container ">
    <form class="starred js-social-form" action="/goat-community/goat/unstar" accept-charset="UTF-8" method="post"><input type="hidden" name="authenticity_token" value="mCVkzuvxVMw50mOAQgHutbQaMSjszLsVJrp4kFspgtErgowejp/Cm/atrUy6dGi/w0chlGIYrru/wAsfKEkvcw==" />
      <input type="hidden" name="context" value="repository"></input>
      <button type="submit" class="btn btn-sm btn-with-count  js-toggler-target" aria-label="Unstar this repository" title="Unstar goat-community/goat" data-hydro-click="{&quot;event_type&quot;:&quot;repository.click&quot;,&quot;payload&quot;:{&quot;target&quot;:&quot;UNSTAR_BUTTON&quot;,&quot;repository_id&quot;:150960118,&quot;originating_url&quot;:&quot;https://github.com/goat-community/goat/blob/main/app/database/data_preparation/SQL/pois.sql&quot;,&quot;user_id&quot;:58067217}}" data-hydro-click-hmac="515d8dbd147cc06843498a03fdf0ee77c0eb63352da1933f7343b34fc143302d" data-ga-click="Repository, click unstar button, action:blob#show; text:Unstar">        <svg height="16" class="octicon octicon-star-fill" viewBox="0 0 16 16" version="1.1" width="16" aria-hidden="true"><path fill-rule="evenodd" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25z"></path></svg>
        Unstar
</button>        <a class="social-count js-social-count" href="/goat-community/goat/stargazers"
           aria-label="15 users starred this repository">
           15
        </a>
</form>
    <form class="unstarred js-social-form" action="/goat-community/goat/star" accept-charset="UTF-8" method="post"><input type="hidden" name="authenticity_token" value="qQ8Dp4VWVSfnzekvsGAIN27xseSvrpOSfQtu/S+1pXyQqQoCX8wrRGa7XKpM/buazKovZq2J2AwvMe7zMX7RUQ==" />
      <input type="hidden" name="context" value="repository"></input>
      <button type="submit" class="btn btn-sm btn-with-count  js-toggler-target" aria-label="Unstar this repository" title="Star goat-community/goat" data-hydro-click="{&quot;event_type&quot;:&quot;repository.click&quot;,&quot;payload&quot;:{&quot;target&quot;:&quot;STAR_BUTTON&quot;,&quot;repository_id&quot;:150960118,&quot;originating_url&quot;:&quot;https://github.com/goat-community/goat/blob/main/app/database/data_preparation/SQL/pois.sql&quot;,&quot;user_id&quot;:58067217}}" data-hydro-click-hmac="c426180af8db0f90767b7bea5307c6688044869892e501ceb6ce36c8bd1d4da6" data-ga-click="Repository, click star button, action:blob#show; text:Star">        <svg height="16" class="octicon octicon-star" viewBox="0 0 16 16" version="1.1" width="16" aria-hidden="true"><path fill-rule="evenodd" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.21.612a.75.75 0 01.416 1.279l-3.046 2.97.719 4.192a.75.75 0 01-1.088.791L8 12.347l-3.766 1.98a.75.75 0 01-1.088-.79l.72-4.194L.818 6.374a.75.75 0 01.416-1.28l4.21-.611L7.327.668A.75.75 0 018 .25zm0 2.445L6.615 5.5a.75.75 0 01-.564.41l-3.097.45 2.24 2.184a.75.75 0 01.216.664l-.528 3.084 2.769-1.456a.75.75 0 01.698 0l2.77 1.456-.53-3.084a.75.75 0 01.216-.664l2.24-2.183-3.096-.45a.75.75 0 01-.564-.41L8 2.694v.001z"></path></svg>
        Star
</button>        <a class="social-count js-social-count" href="/goat-community/goat/stargazers"
           aria-label="15 users starred this repository">
          15
        </a>
</form>  </div>

  </li>

  <li>
          <!-- '"` --><!-- </textarea></xmp> --></option></form><form class="btn-with-count" action="/goat-community/goat/fork" accept-charset="UTF-8" method="post"><input type="hidden" name="authenticity_token" value="1FmOqNiKb2NXTTReQxiAh5sy9GoAMBgy8wDGX2f/PXtoksXSTrEvhRcugIsg1tFnIsXSEM2L2uxoRhd8GqzwLA==" />
            <button class="btn btn-sm btn-with-count" data-hydro-click="{&quot;event_type&quot;:&quot;repository.click&quot;,&quot;payload&quot;:{&quot;target&quot;:&quot;FORK_BUTTON&quot;,&quot;repository_id&quot;:150960118,&quot;originating_url&quot;:&quot;https://github.com/goat-community/goat/blob/main/app/database/data_preparation/SQL/pois.sql&quot;,&quot;user_id&quot;:58067217}}" data-hydro-click-hmac="c42affb996d39d362f9ea53c5fdcb1412134d9ed9aa19c2dd667b0aa8c814840" data-ga-click="Repository, show fork modal, action:blob#show; text:Fork" type="submit" title="Fork your own copy of goat-community/goat to your account" aria-label="Fork your own copy of goat-community/goat to your account">              <svg class="octicon octicon-repo-forked" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M5 3.25a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm0 2.122a2.25 2.25 0 10-1.5 0v.878A2.25 2.25 0 005.75 8.5h1.5v2.128a2.251 2.251 0 101.5 0V8.5h1.5a2.25 2.25 0 002.25-2.25v-.878a2.25 2.25 0 10-1.5 0v.878a.75.75 0 01-.75.75h-4.5A.75.75 0 015 6.25v-.878zm3.75 7.378a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm3-8.75a.75.75 0 100-1.5.75.75 0 000 1.5z"></path></svg>
              Fork
</button></form>
    <a href="/goat-community/goat/network/members" class="social-count"
       aria-label="15 users forked this repository">
      15
    </a>
  </li>
</ul>

    </div>
    
<nav aria-label="Repository" data-pjax="#js-repo-pjax-container" class="js-repo-nav js-sidenav-container-pjax js-responsive-underlinenav overflow-hidden UnderlineNav px-3 px-md-4 px-lg-5 bg-gray-light">
  <ul class="UnderlineNav-body list-style-none ">
          <li class="d-flex">
        <a class="js-selected-navigation-item selected UnderlineNav-item hx_underlinenav-item no-wrap js-responsive-underlinenav-item" data-tab-item="code-tab" data-hotkey="g c" data-ga-click="Repository, Navigation click, Code tab" aria-current="page" data-selected-links="repo_source repo_downloads repo_commits repo_releases repo_tags repo_branches repo_packages repo_deployments /goat-community/goat" href="/goat-community/goat">
              <svg classes="UnderlineNav-octicon" display="none inline" height="16" class="octicon octicon-code UnderlineNav-octicon d-none d-sm-inline" viewBox="0 0 16 16" version="1.1" width="16" aria-hidden="true"><path fill-rule="evenodd" d="M4.72 3.22a.75.75 0 011.06 1.06L2.06 8l3.72 3.72a.75.75 0 11-1.06 1.06L.47 8.53a.75.75 0 010-1.06l4.25-4.25zm6.56 0a.75.75 0 10-1.06 1.06L13.94 8l-3.72 3.72a.75.75 0 101.06 1.06l4.25-4.25a.75.75 0 000-1.06l-4.25-4.25z"></path></svg>
            <span data-content="Code">Code</span>
              <span title="Not available" class="Counter "></span>
</a>      </li>
      <li class="d-flex">
        <a class="js-selected-navigation-item UnderlineNav-item hx_underlinenav-item no-wrap js-responsive-underlinenav-item" data-tab-item="issues-tab" data-hotkey="g i" data-ga-click="Repository, Navigation click, Issues tab" data-selected-links="repo_issues repo_labels repo_milestones /goat-community/goat/issues" href="/goat-community/goat/issues">
              <svg classes="UnderlineNav-octicon" display="none inline" height="16" class="octicon octicon-issue-opened UnderlineNav-octicon d-none d-sm-inline" viewBox="0 0 16 16" version="1.1" width="16" aria-hidden="true"><path fill-rule="evenodd" d="M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8zm9 3a1 1 0 11-2 0 1 1 0 012 0zm-.25-6.25a.75.75 0 00-1.5 0v3.5a.75.75 0 001.5 0v-3.5z"></path></svg>
            <span data-content="Issues">Issues</span>
              <span title="83" class="Counter ">83</span>
</a>      </li>
      <li class="d-flex">
        <a class="js-selected-navigation-item UnderlineNav-item hx_underlinenav-item no-wrap js-responsive-underlinenav-item" data-tab-item="pull-requests-tab" data-hotkey="g p" data-ga-click="Repository, Navigation click, Pull requests tab" data-selected-links="repo_pulls checks /goat-community/goat/pulls" href="/goat-community/goat/pulls">
              <svg classes="UnderlineNav-octicon" display="none inline" height="16" class="octicon octicon-git-pull-request UnderlineNav-octicon d-none d-sm-inline" viewBox="0 0 16 16" version="1.1" width="16" aria-hidden="true"><path fill-rule="evenodd" d="M7.177 3.073L9.573.677A.25.25 0 0110 .854v4.792a.25.25 0 01-.427.177L7.177 3.427a.25.25 0 010-.354zM3.75 2.5a.75.75 0 100 1.5.75.75 0 000-1.5zm-2.25.75a2.25 2.25 0 113 2.122v5.256a2.251 2.251 0 11-1.5 0V5.372A2.25 2.25 0 011.5 3.25zM11 2.5h-1V4h1a1 1 0 011 1v5.628a2.251 2.251 0 101.5 0V5A2.5 2.5 0 0011 2.5zm1 10.25a.75.75 0 111.5 0 .75.75 0 01-1.5 0zM3.75 12a.75.75 0 100 1.5.75.75 0 000-1.5z"></path></svg>
            <span data-content="Pull requests">Pull requests</span>
              <span title="2" class="Counter ">2</span>
</a>      </li>
      <li class="d-flex">
        <a class="js-selected-navigation-item UnderlineNav-item hx_underlinenav-item no-wrap js-responsive-underlinenav-item" data-tab-item="actions-tab" data-hotkey="g a" data-ga-click="Repository, Navigation click, Actions tab" data-selected-links="repo_actions /goat-community/goat/actions" href="/goat-community/goat/actions">
              <svg classes="UnderlineNav-octicon" display="none inline" height="16" class="octicon octicon-play UnderlineNav-octicon d-none d-sm-inline" viewBox="0 0 16 16" version="1.1" width="16" aria-hidden="true"><path fill-rule="evenodd" d="M1.5 8a6.5 6.5 0 1113 0 6.5 6.5 0 01-13 0zM8 0a8 8 0 100 16A8 8 0 008 0zM6.379 5.227A.25.25 0 006 5.442v5.117a.25.25 0 00.379.214l4.264-2.559a.25.25 0 000-.428L6.379 5.227z"></path></svg>
            <span data-content="Actions">Actions</span>
              <span title="Not available" class="Counter "></span>
</a>      </li>
      <li class="d-flex">
        <a class="js-selected-navigation-item UnderlineNav-item hx_underlinenav-item no-wrap js-responsive-underlinenav-item" data-tab-item="projects-tab" data-hotkey="g b" data-ga-click="Repository, Navigation click, Projects tab" data-selected-links="repo_projects new_repo_project repo_project /goat-community/goat/projects" href="/goat-community/goat/projects">
              <svg classes="UnderlineNav-octicon" display="none inline" height="16" class="octicon octicon-project UnderlineNav-octicon d-none d-sm-inline" viewBox="0 0 16 16" version="1.1" width="16" aria-hidden="true"><path fill-rule="evenodd" d="M1.75 0A1.75 1.75 0 000 1.75v12.5C0 15.216.784 16 1.75 16h12.5A1.75 1.75 0 0016 14.25V1.75A1.75 1.75 0 0014.25 0H1.75zM1.5 1.75a.25.25 0 01.25-.25h12.5a.25.25 0 01.25.25v12.5a.25.25 0 01-.25.25H1.75a.25.25 0 01-.25-.25V1.75zM11.75 3a.75.75 0 00-.75.75v7.5a.75.75 0 001.5 0v-7.5a.75.75 0 00-.75-.75zm-8.25.75a.75.75 0 011.5 0v5.5a.75.75 0 01-1.5 0v-5.5zM8 3a.75.75 0 00-.75.75v3.5a.75.75 0 001.5 0v-3.5A.75.75 0 008 3z"></path></svg>
            <span data-content="Projects">Projects</span>
              <span title="0" hidden="hidden" class="Counter ">0</span>
</a>      </li>
      <li class="d-flex">
        <a class="js-selected-navigation-item UnderlineNav-item hx_underlinenav-item no-wrap js-responsive-underlinenav-item" data-tab-item="wiki-tab" data-hotkey="g w" data-ga-click="Repository, Navigation click, Wikis tab" data-selected-links="repo_wiki /goat-community/goat/wiki" href="/goat-community/goat/wiki">
              <svg classes="UnderlineNav-octicon" display="none inline" height="16" class="octicon octicon-book UnderlineNav-octicon d-none d-sm-inline" viewBox="0 0 16 16" version="1.1" width="16" aria-hidden="true"><path fill-rule="evenodd" d="M0 1.75A.75.75 0 01.75 1h4.253c1.227 0 2.317.59 3 1.501A3.744 3.744 0 0111.006 1h4.245a.75.75 0 01.75.75v10.5a.75.75 0 01-.75.75h-4.507a2.25 2.25 0 00-1.591.659l-.622.621a.75.75 0 01-1.06 0l-.622-.621A2.25 2.25 0 005.258 13H.75a.75.75 0 01-.75-.75V1.75zm8.755 3a2.25 2.25 0 012.25-2.25H14.5v9h-3.757c-.71 0-1.4.201-1.992.572l.004-7.322zm-1.504 7.324l.004-5.073-.002-2.253A2.25 2.25 0 005.003 2.5H1.5v9h3.757a3.75 3.75 0 011.994.574z"></path></svg>
            <span data-content="Wiki">Wiki</span>
              <span title="Not available" class="Counter "></span>
</a>      </li>
      <li class="d-flex">
        <a class="js-selected-navigation-item UnderlineNav-item hx_underlinenav-item no-wrap js-responsive-underlinenav-item" data-tab-item="security-tab" data-hotkey="g s" data-ga-click="Repository, Navigation click, Security tab" data-selected-links="security overview alerts policy token_scanning code_scanning /goat-community/goat/security" href="/goat-community/goat/security">
              <svg classes="UnderlineNav-octicon" display="none inline" height="16" class="octicon octicon-shield UnderlineNav-octicon d-none d-sm-inline" viewBox="0 0 16 16" version="1.1" width="16" aria-hidden="true"><path fill-rule="evenodd" d="M7.467.133a1.75 1.75 0 011.066 0l5.25 1.68A1.75 1.75 0 0115 3.48V7c0 1.566-.32 3.182-1.303 4.682-.983 1.498-2.585 2.813-5.032 3.855a1.7 1.7 0 01-1.33 0c-2.447-1.042-4.049-2.357-5.032-3.855C1.32 10.182 1 8.566 1 7V3.48a1.75 1.75 0 011.217-1.667l5.25-1.68zm.61 1.429a.25.25 0 00-.153 0l-5.25 1.68a.25.25 0 00-.174.238V7c0 1.358.275 2.666 1.057 3.86.784 1.194 2.121 2.34 4.366 3.297a.2.2 0 00.154 0c2.245-.956 3.582-2.104 4.366-3.298C13.225 9.666 13.5 8.36 13.5 7V3.48a.25.25 0 00-.174-.237l-5.25-1.68zM9 10.5a1 1 0 11-2 0 1 1 0 012 0zm-.25-5.75a.75.75 0 10-1.5 0v3a.75.75 0 001.5 0v-3z"></path></svg>
            <span data-content="Security">Security</span>
              <span data-url="/goat-community/goat/security/overall-count" title="Not available" class="js-security-tab-count Counter "></span>
</a>      </li>
      <li class="d-flex">
        <a class="js-selected-navigation-item UnderlineNav-item hx_underlinenav-item no-wrap js-responsive-underlinenav-item" data-tab-item="insights-tab" data-ga-click="Repository, Navigation click, Insights tab" data-selected-links="repo_graphs repo_contributors dependency_graph dependabot_updates pulse people /goat-community/goat/pulse" href="/goat-community/goat/pulse">
              <svg classes="UnderlineNav-octicon" display="none inline" height="16" class="octicon octicon-graph UnderlineNav-octicon d-none d-sm-inline" viewBox="0 0 16 16" version="1.1" width="16" aria-hidden="true"><path fill-rule="evenodd" d="M1.5 1.75a.75.75 0 00-1.5 0v12.5c0 .414.336.75.75.75h14.5a.75.75 0 000-1.5H1.5V1.75zm14.28 2.53a.75.75 0 00-1.06-1.06L10 7.94 7.53 5.47a.75.75 0 00-1.06 0L3.22 8.72a.75.75 0 001.06 1.06L7 7.06l2.47 2.47a.75.75 0 001.06 0l5.25-5.25z"></path></svg>
            <span data-content="Insights">Insights</span>
              <span title="Not available" class="Counter "></span>
</a>      </li>

</ul>        <div class="position-absolute right-0 pr-3 pr-md-4 pr-lg-5 js-responsive-underlinenav-overflow" style="visibility:hidden;">
      <details class="details-overlay details-reset position-relative">
  <summary role="button">
              <div class="UnderlineNav-item mr-0 border-0">
            <svg class="octicon octicon-kebab-horizontal" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path d="M8 9a1.5 1.5 0 100-3 1.5 1.5 0 000 3zM1.5 9a1.5 1.5 0 100-3 1.5 1.5 0 000 3zm13 0a1.5 1.5 0 100-3 1.5 1.5 0 000 3z"></path></svg>
            <span class="sr-only">More</span>
          </div>

</summary>            <details-menu role="menu" class="dropdown-menu dropdown-menu-sw ">
  
            <ul>
                <li data-menu-item="code-tab" hidden>
                  <a role="menuitem" class="js-selected-navigation-item dropdown-item" data-selected-links=" /goat-community/goat" href="/goat-community/goat">
                    Code
</a>                </li>
                <li data-menu-item="issues-tab" hidden>
                  <a role="menuitem" class="js-selected-navigation-item dropdown-item" data-selected-links=" /goat-community/goat/issues" href="/goat-community/goat/issues">
                    Issues
</a>                </li>
                <li data-menu-item="pull-requests-tab" hidden>
                  <a role="menuitem" class="js-selected-navigation-item dropdown-item" data-selected-links=" /goat-community/goat/pulls" href="/goat-community/goat/pulls">
                    Pull requests
</a>                </li>
                <li data-menu-item="actions-tab" hidden>
                  <a role="menuitem" class="js-selected-navigation-item dropdown-item" data-selected-links=" /goat-community/goat/actions" href="/goat-community/goat/actions">
                    Actions
</a>                </li>
                <li data-menu-item="projects-tab" hidden>
                  <a role="menuitem" class="js-selected-navigation-item dropdown-item" data-selected-links=" /goat-community/goat/projects" href="/goat-community/goat/projects">
                    Projects
</a>                </li>
                <li data-menu-item="wiki-tab" hidden>
                  <a role="menuitem" class="js-selected-navigation-item dropdown-item" data-selected-links=" /goat-community/goat/wiki" href="/goat-community/goat/wiki">
                    Wiki
</a>                </li>
                <li data-menu-item="security-tab" hidden>
                  <a role="menuitem" class="js-selected-navigation-item dropdown-item" data-selected-links=" /goat-community/goat/security" href="/goat-community/goat/security">
                    Security
</a>                </li>
                <li data-menu-item="insights-tab" hidden>
                  <a role="menuitem" class="js-selected-navigation-item dropdown-item" data-selected-links=" /goat-community/goat/pulse" href="/goat-community/goat/pulse">
                    Insights
</a>                </li>
            </ul>

</details-menu>
</details>    </div>

</nav>
  </div>

<div class="container-xl clearfix new-discussion-timeline  px-3 px-md-4 px-lg-5">
  <div class="repository-content " >

    
    
  


    <a class="d-none js-permalink-shortcut" data-hotkey="y" href="/goat-community/goat/blob/d429666efd81bc4dfd8a1f8425f51bdf7eafcd2c/app/database/data_preparation/SQL/pois.sql">Permalink</a>

    <!-- blob contrib key: blob_contributors:v22:545430f95e12cf40cb8426e5dda434a3 -->
    

    <div class="d-flex flex-items-start flex-shrink-0 pb-3 flex-wrap flex-md-nowrap flex-justify-between flex-md-justify-start">
      
<div class="position-relative">
  <details class="details-reset details-overlay mr-0 mb-0 " id="branch-select-menu">
    <summary class="btn css-truncate"
            data-hotkey="w"
            title="Switch branches or tags">
      <svg text="gray" height="16" class="octicon octicon-git-branch text-gray" viewBox="0 0 16 16" version="1.1" width="16" aria-hidden="true"><path fill-rule="evenodd" d="M11.75 2.5a.75.75 0 100 1.5.75.75 0 000-1.5zm-2.25.75a2.25 2.25 0 113 2.122V6A2.5 2.5 0 0110 8.5H6a1 1 0 00-1 1v1.128a2.251 2.251 0 11-1.5 0V5.372a2.25 2.25 0 111.5 0v1.836A2.492 2.492 0 016 7h4a1 1 0 001-1v-.628A2.25 2.25 0 019.5 3.25zM4.25 12a.75.75 0 100 1.5.75.75 0 000-1.5zM3.5 3.25a.75.75 0 111.5 0 .75.75 0 01-1.5 0z"></path></svg>
      <span class="css-truncate-target" data-menu-button>main</span>
      <span class="dropdown-caret"></span>
    </summary>

    <details-menu class="SelectMenu SelectMenu--hasFilter" src="/goat-community/goat/refs/main/app/database/data_preparation/SQL/pois.sql?source_action=show&amp;source_controller=blob" preload>
      <div class="SelectMenu-modal">
        <include-fragment class="SelectMenu-loading" aria-label="Menu is loading">
          <svg class="octicon octicon-octoface anim-pulse" height="32" viewBox="0 0 24 24" version="1.1" width="32" aria-hidden="true"><path d="M7.75 11c-.69 0-1.25.56-1.25 1.25v1.5a1.25 1.25 0 102.5 0v-1.5C9 11.56 8.44 11 7.75 11zm1.27 4.5a.469.469 0 01.48-.5h5a.47.47 0 01.48.5c-.116 1.316-.759 2.5-2.98 2.5s-2.864-1.184-2.98-2.5zm7.23-4.5c-.69 0-1.25.56-1.25 1.25v1.5a1.25 1.25 0 102.5 0v-1.5c0-.69-.56-1.25-1.25-1.25z"></path><path fill-rule="evenodd" d="M21.255 3.82a1.725 1.725 0 00-2.141-1.195c-.557.16-1.406.44-2.264.866-.78.386-1.647.93-2.293 1.677A18.442 18.442 0 0012 5c-.93 0-1.784.059-2.569.17-.645-.74-1.505-1.28-2.28-1.664a13.876 13.876 0 00-2.265-.866 1.725 1.725 0 00-2.141 1.196 23.645 23.645 0 00-.69 3.292c-.125.97-.191 2.07-.066 3.112C1.254 11.882 1 13.734 1 15.527 1 19.915 3.13 23 12 23c8.87 0 11-3.053 11-7.473 0-1.794-.255-3.647-.99-5.29.127-1.046.06-2.15-.066-3.125a23.652 23.652 0 00-.689-3.292zM20.5 14c.5 3.5-1.5 6.5-8.5 6.5s-9-3-8.5-6.5c.583-4 3-6 8.5-6s7.928 2 8.5 6z"></path></svg>
        </include-fragment>
      </div>
    </details-menu>
  </details>

</div>

      <h2 id="blob-path" class="breadcrumb flex-auto min-width-0 text-normal mx-0 mx-md-3 width-full width-md-auto flex-order-1 flex-md-order-none mt-3 mt-md-0">
        <span class="js-repo-root text-bold"><span class="js-path-segment d-inline-block wb-break-all"><a data-pjax="true" href="/goat-community/goat"><span>goat</span></a></span></span><span class="separator">/</span><span class="js-path-segment d-inline-block wb-break-all"><a data-pjax="true" href="/goat-community/goat/tree/main/app"><span>app</span></a></span><span class="separator">/</span><span class="js-path-segment d-inline-block wb-break-all"><a data-pjax="true" href="/goat-community/goat/tree/main/app/database"><span>database</span></a></span><span class="separator">/</span><span class="js-path-segment d-inline-block wb-break-all"><a data-pjax="true" href="/goat-community/goat/tree/main/app/database/data_preparation"><span>data_preparation</span></a></span><span class="separator">/</span><span class="js-path-segment d-inline-block wb-break-all"><a data-pjax="true" href="/goat-community/goat/tree/main/app/database/data_preparation/SQL"><span>SQL</span></a></span><span class="separator">/</span><strong class="final-path">pois.sql</strong>
      </h2>
      <a href="/goat-community/goat/find/main"
            class="js-pjax-capture-input btn mr-2 d-none d-md-block"
            data-pjax
            data-hotkey="t">
        Go to file
      </a>

      <details id="blob-more-options-details" class="details-overlay details-reset position-relative">
  <summary role="button">
              <span class="btn">
            <svg aria-label="More options" height="16" class="octicon octicon-kebab-horizontal" viewBox="0 0 16 16" version="1.1" width="16" role="img"><path d="M8 9a1.5 1.5 0 100-3 1.5 1.5 0 000 3zM1.5 9a1.5 1.5 0 100-3 1.5 1.5 0 000 3zm13 0a1.5 1.5 0 100-3 1.5 1.5 0 000 3z"></path></svg>
          </span>

</summary>            <ul class="dropdown-menu dropdown-menu-sw">
            <li class="d-block d-md-none">
              <a class="dropdown-item d-flex flex-items-baseline" data-hydro-click="{&quot;event_type&quot;:&quot;repository.click&quot;,&quot;payload&quot;:{&quot;target&quot;:&quot;FIND_FILE_BUTTON&quot;,&quot;repository_id&quot;:150960118,&quot;originating_url&quot;:&quot;https://github.com/goat-community/goat/blob/main/app/database/data_preparation/SQL/pois.sql&quot;,&quot;user_id&quot;:58067217}}" data-hydro-click-hmac="3a99f7a83caa60ca0fe60badb86295e463879c07862c18f3f6ffe01d083e8df2" data-ga-click="Repository, find file, location:repo overview" data-hotkey="t" data-pjax="true" href="/goat-community/goat/find/main">
                <span class="flex-auto">Go to file</span>
                <span class="text-small text-gray" aria-hidden="true">T</span>
</a>            </li>
            <li data-toggle-for="blob-more-options-details">
              <button type="button" data-toggle-for="jumpto-line-details-dialog" class="btn-link dropdown-item">
                <span class="d-flex flex-items-baseline">
                  <span class="flex-auto">Go to line</span>
                  <span class="text-small text-gray" aria-hidden="true">L</span>
                </span>
              </button>
            </li>
            <li class="dropdown-divider" role="none"></li>
            <li>
              <clipboard-copy value="app/database/data_preparation/SQL/pois.sql" class="dropdown-item cursor-pointer" data-toggle-for="blob-more-options-details">
                Copy path
              </clipboard-copy>
            </li>
          </ul>

</details>    </div>



    <div class="Box d-flex flex-column flex-shrink-0 mb-3">
      <include-fragment src="/goat-community/goat/contributors/main/app/database/data_preparation/SQL/pois.sql" class="commit-loader">
        <div class="Box-header Box-header--blue d-flex flex-items-center">
          <div class="Skeleton avatar avatar-user flex-shrink-0 ml-n1 mr-n1 mt-n1 mb-n1" style="width:24px;height:24px;"></div>
          <div class="Skeleton Skeleton--text col-5 ml-2">&nbsp;</div>
        </div>

        <div class="Box-body d-flex flex-items-center" >
          <div class="Skeleton Skeleton--text col-1">&nbsp;</div>
          <span class="text-red h6 loader-error">Cannot retrieve contributors at this time</span>
        </div>
</include-fragment>    </div>






    <div class="Box mt-3 position-relative
      ">
      
<div class="Box-header py-2 d-flex flex-column flex-shrink-0 flex-md-row flex-md-items-center">
  <div class="text-mono f6 flex-auto pr-3 flex-order-2 flex-md-order-1 mt-2 mt-md-0">

      500 lines (412 sloc)
      <span class="file-info-divider"></span>
    24 KB
  </div>

  <div class="d-flex py-1 py-md-0 flex-auto flex-order-1 flex-md-order-2 flex-sm-grow-0 flex-justify-between">

    <div class="BtnGroup">
      <a href="/goat-community/goat/raw/main/app/database/data_preparation/SQL/pois.sql" id="raw-url" role="button" class="btn btn-sm BtnGroup-item ">Raw</a>
        <a href="/goat-community/goat/blame/main/app/database/data_preparation/SQL/pois.sql" data-hotkey="b" role="button" class="btn js-update-url-with-hash btn-sm BtnGroup-item ">Blame</a>
    </div>

    <div>
          <a class="btn-octicon tooltipped tooltipped-nw js-remove-unless-platform"
             data-platforms="windows,mac"
             href="x-github-client://openRepo/https://github.com/goat-community/goat?branch=main&amp;filepath=app%2Fdatabase%2Fdata_preparation%2FSQL%2Fpois.sql"
             aria-label="Open this file in GitHub Desktop"
             data-ga-click="Repository, open with desktop">
              <svg class="octicon octicon-device-desktop" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M1.75 2.5h12.5a.25.25 0 01.25.25v7.5a.25.25 0 01-.25.25H1.75a.25.25 0 01-.25-.25v-7.5a.25.25 0 01.25-.25zM14.25 1H1.75A1.75 1.75 0 000 2.75v7.5C0 11.216.784 12 1.75 12h3.727c-.1 1.041-.52 1.872-1.292 2.757A.75.75 0 004.75 16h6.5a.75.75 0 00.565-1.243c-.772-.885-1.193-1.716-1.292-2.757h3.727A1.75 1.75 0 0016 10.25v-7.5A1.75 1.75 0 0014.25 1zM9.018 12H6.982a5.72 5.72 0 01-.765 2.5h3.566a5.72 5.72 0 01-.765-2.5z"></path></svg>
          </a>

          <!-- '"` --><!-- </textarea></xmp> --></option></form><form class="inline-form js-update-url-with-hash" action="/goat-community/goat/edit/main/app/database/data_preparation/SQL/pois.sql" accept-charset="UTF-8" method="post"><input type="hidden" name="authenticity_token" value="4UP/8P1MGl9KfpxnM1NaOlIyldgByy1DvaomYUJqNlKIsNKiI1CH5e/BoO9UbSV7Lh9YWxCgP6SRLN5kyi6pVw==" />
            <button class="btn-octicon tooltipped tooltipped-nw" type="submit"
              aria-label="Edit the file in your fork of this project" data-hotkey="e" data-disable-with>
              <svg class="octicon octicon-pencil" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M11.013 1.427a1.75 1.75 0 012.474 0l1.086 1.086a1.75 1.75 0 010 2.474l-8.61 8.61c-.21.21-.47.364-.756.445l-3.251.93a.75.75 0 01-.927-.928l.929-3.25a1.75 1.75 0 01.445-.758l8.61-8.61zm1.414 1.06a.25.25 0 00-.354 0L10.811 3.75l1.439 1.44 1.263-1.263a.25.25 0 000-.354l-1.086-1.086zM11.189 6.25L9.75 4.81l-6.286 6.287a.25.25 0 00-.064.108l-.558 1.953 1.953-.558a.249.249 0 00.108-.064l6.286-6.286z"></path></svg>
            </button>
</form>
          <!-- '"` --><!-- </textarea></xmp> --></option></form><form class="inline-form" action="/goat-community/goat/delete/main/app/database/data_preparation/SQL/pois.sql" accept-charset="UTF-8" method="post"><input type="hidden" name="authenticity_token" value="vngFF5eP0CLLDxM18aRrumgSbHKaUjvZm2lA+rkDNyv/AOTWPcEGLaewQEnvLfbJPfiHf8yH82RHACpLfeKahA==" />
            <button class="btn-octicon btn-octicon-danger tooltipped tooltipped-nw" type="submit"
              aria-label="Delete the file in your fork of this project" data-disable-with>
              <svg class="octicon octicon-trashcan" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M6.5 1.75a.25.25 0 01.25-.25h2.5a.25.25 0 01.25.25V3h-3V1.75zm4.5 0V3h2.25a.75.75 0 010 1.5H2.75a.75.75 0 010-1.5H5V1.75C5 .784 5.784 0 6.75 0h2.5C10.216 0 11 .784 11 1.75zM4.496 6.675a.75.75 0 10-1.492.15l.66 6.6A1.75 1.75 0 005.405 15h5.19c.9 0 1.652-.681 1.741-1.576l.66-6.6a.75.75 0 00-1.492-.149l-.66 6.6a.25.25 0 01-.249.225h-5.19a.25.25 0 01-.249-.225l-.66-6.6z"></path></svg>
            </button>
</form>    </div>
  </div>
</div>



      

  <div itemprop="text" class="Box-body p-0 blob-wrapper data type-sql  gist-border-0">
      
<table class="highlight tab-size js-file-line-container" data-tab-size="8" data-paste-markdown-skip>
      <tr>
        <td id="L1" class="blob-num js-line-number" data-line-number="1"></td>
        <td id="LC1" class="blob-code blob-code-inner js-file-line"><span class="pl-k">DROP</span> <span class="pl-k">TABLE</span> IF EXISTS pois CASCADE;</td>
      </tr>
      <tr>
        <td id="L2" class="blob-num js-line-number" data-line-number="2"></td>
        <td id="LC2" class="blob-code blob-code-inner js-file-line"><span class="pl-k">CREATE</span> <span class="pl-k">TABLE</span> <span class="pl-en">pois</span> <span class="pl-k">as</span> (</td>
      </tr>
      <tr>
        <td id="L3" class="blob-num js-line-number" data-line-number="3"></td>
        <td id="LC3" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L4" class="blob-num js-line-number" data-line-number="4"></td>
        <td id="LC4" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L5" class="blob-num js-line-number" data-line-number="5"></td>
        <td id="LC5" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span> all amenities, excluding shops, schools and kindergartens</span></td>
      </tr>
      <tr>
        <td id="L6" class="blob-num js-line-number" data-line-number="6"></td>
        <td id="LC6" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> osm_id,<span class="pl-s"><span class="pl-pds">&#39;</span>point<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> origin_geometry, access,<span class="pl-s"><span class="pl-pds">&quot;</span>addr:housenumber<span class="pl-pds">&quot;</span></span> <span class="pl-k">as</span> housenumber, amenity, shop, </td>
      </tr>
      <tr>
        <td id="L7" class="blob-num js-line-number" data-line-number="7"></td>
        <td id="LC7" class="blob-code blob-code-inner js-file-line">tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>origin<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin, tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>organic<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> organic, denomination,brand,name,</td>
      </tr>
      <tr>
        <td id="L8" class="blob-num js-line-number" data-line-number="8"></td>
        <td id="LC8" class="blob-code blob-code-inner js-file-line">operator,public_transport,railway,religion,tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>opening_hours<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> opening_hours, ref,tags, way <span class="pl-k">as</span> geom, tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> wheelchair  </td>
      </tr>
      <tr>
        <td id="L9" class="blob-num js-line-number" data-line-number="9"></td>
        <td id="LC9" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> planet_osm_point</td>
      </tr>
      <tr>
        <td id="L10" class="blob-num js-line-number" data-line-number="10"></td>
        <td id="LC10" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> amenity <span class="pl-k">IS NOT NULL</span> <span class="pl-k">AND</span> shop IS <span class="pl-k">NULL</span> <span class="pl-k">AND</span> amenity <span class="pl-k">&lt;&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>school<span class="pl-pds">&#39;</span></span> <span class="pl-k">AND</span> amenity <span class="pl-k">&lt;&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>kindergarten<span class="pl-pds">&#39;</span></span></td>
      </tr>
      <tr>
        <td id="L11" class="blob-num js-line-number" data-line-number="11"></td>
        <td id="LC11" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L12" class="blob-num js-line-number" data-line-number="12"></td>
        <td id="LC12" class="blob-code blob-code-inner js-file-line"><span class="pl-k">UNION ALL</span></td>
      </tr>
      <tr>
        <td id="L13" class="blob-num js-line-number" data-line-number="13"></td>
        <td id="LC13" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span> same block to edit--</span></td>
      </tr>
      <tr>
        <td id="L14" class="blob-num js-line-number" data-line-number="14"></td>
        <td id="LC14" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L15" class="blob-num js-line-number" data-line-number="15"></td>
        <td id="LC15" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span>all playgrounds (insert leisure as amenity)</span></td>
      </tr>
      <tr>
        <td id="L16" class="blob-num js-line-number" data-line-number="16"></td>
        <td id="LC16" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L17" class="blob-num js-line-number" data-line-number="17"></td>
        <td id="LC17" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> osm_id,<span class="pl-s"><span class="pl-pds">&#39;</span>point<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> origin_geometry, access,<span class="pl-s"><span class="pl-pds">&quot;</span>addr:housenumber<span class="pl-pds">&quot;</span></span> <span class="pl-k">as</span> housenumber, leisure <span class="pl-k">AS</span> amenity, shop, </td>
      </tr>
      <tr>
        <td id="L18" class="blob-num js-line-number" data-line-number="18"></td>
        <td id="LC18" class="blob-code blob-code-inner js-file-line">tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>origin<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin, tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>organic<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> organic, denomination,brand,name,</td>
      </tr>
      <tr>
        <td id="L19" class="blob-num js-line-number" data-line-number="19"></td>
        <td id="LC19" class="blob-code blob-code-inner js-file-line">operator,public_transport,railway,religion,tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>opening_hours<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> opening_hours, ref,tags, way <span class="pl-k">as</span> geom, tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> wheelchair  </td>
      </tr>
      <tr>
        <td id="L20" class="blob-num js-line-number" data-line-number="20"></td>
        <td id="LC20" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> planet_osm_point</td>
      </tr>
      <tr>
        <td id="L21" class="blob-num js-line-number" data-line-number="21"></td>
        <td id="LC21" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> leisure <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>playground<span class="pl-pds">&#39;</span></span></td>
      </tr>
      <tr>
        <td id="L22" class="blob-num js-line-number" data-line-number="22"></td>
        <td id="LC22" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L23" class="blob-num js-line-number" data-line-number="23"></td>
        <td id="LC23" class="blob-code blob-code-inner js-file-line"><span class="pl-k">UNION ALL</span></td>
      </tr>
      <tr>
        <td id="L24" class="blob-num js-line-number" data-line-number="24"></td>
        <td id="LC24" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L25" class="blob-num js-line-number" data-line-number="25"></td>
        <td id="LC25" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> osm_id,<span class="pl-s"><span class="pl-pds">&#39;</span>polygon<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> origin_geometry, access,<span class="pl-s"><span class="pl-pds">&quot;</span>addr:housenumber<span class="pl-pds">&quot;</span></span> <span class="pl-k">as</span> housenumber, leisure <span class="pl-k">AS</span> amenity, shop, </td>
      </tr>
      <tr>
        <td id="L26" class="blob-num js-line-number" data-line-number="26"></td>
        <td id="LC26" class="blob-code blob-code-inner js-file-line">tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>origin<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin, tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>organic<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> organic, denomination,brand,name,</td>
      </tr>
      <tr>
        <td id="L27" class="blob-num js-line-number" data-line-number="27"></td>
        <td id="LC27" class="blob-code blob-code-inner js-file-line">operator,public_transport,railway,religion,tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>opening_hours<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> opening_hours, ref,tags, st_centroid(way) <span class="pl-k">as</span> geom, tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> wheelchair  </td>
      </tr>
      <tr>
        <td id="L28" class="blob-num js-line-number" data-line-number="28"></td>
        <td id="LC28" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> planet_osm_polygon</td>
      </tr>
      <tr>
        <td id="L29" class="blob-num js-line-number" data-line-number="29"></td>
        <td id="LC29" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> leisure <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>playground<span class="pl-pds">&#39;</span></span></td>
      </tr>
      <tr>
        <td id="L30" class="blob-num js-line-number" data-line-number="30"></td>
        <td id="LC30" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L31" class="blob-num js-line-number" data-line-number="31"></td>
        <td id="LC31" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span>end same block</span></td>
      </tr>
      <tr>
        <td id="L32" class="blob-num js-line-number" data-line-number="32"></td>
        <td id="LC32" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L33" class="blob-num js-line-number" data-line-number="33"></td>
        <td id="LC33" class="blob-code blob-code-inner js-file-line"><span class="pl-k">UNION ALL</span> </td>
      </tr>
      <tr>
        <td id="L34" class="blob-num js-line-number" data-line-number="34"></td>
        <td id="LC34" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span> all shops that don&#39;t have an amenity&#39;</span></td>
      </tr>
      <tr>
        <td id="L35" class="blob-num js-line-number" data-line-number="35"></td>
        <td id="LC35" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> osm_id,<span class="pl-s"><span class="pl-pds">&#39;</span>point<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> origin_geometry, access,<span class="pl-s"><span class="pl-pds">&quot;</span>addr:housenumber<span class="pl-pds">&quot;</span></span> <span class="pl-k">as</span> housenumber, amenity, shop, </td>
      </tr>
      <tr>
        <td id="L36" class="blob-num js-line-number" data-line-number="36"></td>
        <td id="LC36" class="blob-code blob-code-inner js-file-line">tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>origin<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin, tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>organic<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> organic, denomination,brand,name,</td>
      </tr>
      <tr>
        <td id="L37" class="blob-num js-line-number" data-line-number="37"></td>
        <td id="LC37" class="blob-code blob-code-inner js-file-line">operator,public_transport,railway,religion,tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>opening_hours<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> opening_hours, ref,tags, way <span class="pl-k">as</span> geom, tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> wheelchair  </td>
      </tr>
      <tr>
        <td id="L38" class="blob-num js-line-number" data-line-number="38"></td>
        <td id="LC38" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> planet_osm_point</td>
      </tr>
      <tr>
        <td id="L39" class="blob-num js-line-number" data-line-number="39"></td>
        <td id="LC39" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> shop <span class="pl-k">IS NOT NULL</span> <span class="pl-k">AND</span> amenity IS <span class="pl-k">NULL</span></td>
      </tr>
      <tr>
        <td id="L40" class="blob-num js-line-number" data-line-number="40"></td>
        <td id="LC40" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L41" class="blob-num js-line-number" data-line-number="41"></td>
        <td id="LC41" class="blob-code blob-code-inner js-file-line"><span class="pl-k">UNION ALL</span> </td>
      </tr>
      <tr>
        <td id="L42" class="blob-num js-line-number" data-line-number="42"></td>
        <td id="LC42" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span> all amenities that are not schools</span></td>
      </tr>
      <tr>
        <td id="L43" class="blob-num js-line-number" data-line-number="43"></td>
        <td id="LC43" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> osm_id, <span class="pl-s"><span class="pl-pds">&#39;</span>polygon<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> origin_geometry, access,<span class="pl-s"><span class="pl-pds">&quot;</span>addr:housenumber<span class="pl-pds">&quot;</span></span> <span class="pl-k">as</span> housenumber, amenity, shop, </td>
      </tr>
      <tr>
        <td id="L44" class="blob-num js-line-number" data-line-number="44"></td>
        <td id="LC44" class="blob-code blob-code-inner js-file-line">tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>origin<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin, tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>organic<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> organic, denomination,brand,name,</td>
      </tr>
      <tr>
        <td id="L45" class="blob-num js-line-number" data-line-number="45"></td>
        <td id="LC45" class="blob-code blob-code-inner js-file-line">operator,public_transport,railway,religion,tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>opening_hours<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> opening_hours, ref,tags, st_centroid(way) <span class="pl-k">as</span> geom, tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> wheelchair  </td>
      </tr>
      <tr>
        <td id="L46" class="blob-num js-line-number" data-line-number="46"></td>
        <td id="LC46" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> planet_osm_polygon</td>
      </tr>
      <tr>
        <td id="L47" class="blob-num js-line-number" data-line-number="47"></td>
        <td id="LC47" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> amenity <span class="pl-k">IS NOT NULL</span> <span class="pl-k">AND</span> amenity <span class="pl-k">&lt;&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>school<span class="pl-pds">&#39;</span></span> <span class="pl-k">AND</span> amenity <span class="pl-k">&lt;&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>kindergarten<span class="pl-pds">&#39;</span></span></td>
      </tr>
      <tr>
        <td id="L48" class="blob-num js-line-number" data-line-number="48"></td>
        <td id="LC48" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L49" class="blob-num js-line-number" data-line-number="49"></td>
        <td id="LC49" class="blob-code blob-code-inner js-file-line"><span class="pl-k">UNION ALL</span> </td>
      </tr>
      <tr>
        <td id="L50" class="blob-num js-line-number" data-line-number="50"></td>
        <td id="LC50" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span> all shops</span></td>
      </tr>
      <tr>
        <td id="L51" class="blob-num js-line-number" data-line-number="51"></td>
        <td id="LC51" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> osm_id,<span class="pl-s"><span class="pl-pds">&#39;</span>polygon<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> origin_geometry, access,<span class="pl-s"><span class="pl-pds">&quot;</span>addr:housenumber<span class="pl-pds">&quot;</span></span> <span class="pl-k">as</span> housenumber, amenity, shop, </td>
      </tr>
      <tr>
        <td id="L52" class="blob-num js-line-number" data-line-number="52"></td>
        <td id="LC52" class="blob-code blob-code-inner js-file-line">tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>origin<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin, tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>organic<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> organic, denomination,brand,name,</td>
      </tr>
      <tr>
        <td id="L53" class="blob-num js-line-number" data-line-number="53"></td>
        <td id="LC53" class="blob-code blob-code-inner js-file-line">operator,public_transport,railway,religion,tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>opening_hours<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> opening_hours, ref,tags, st_centroid(way) <span class="pl-k">as</span> geom, tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> wheelchair  </td>
      </tr>
      <tr>
        <td id="L54" class="blob-num js-line-number" data-line-number="54"></td>
        <td id="LC54" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> planet_osm_polygon</td>
      </tr>
      <tr>
        <td id="L55" class="blob-num js-line-number" data-line-number="55"></td>
        <td id="LC55" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> shop <span class="pl-k">IS NOT NULL</span> </td>
      </tr>
      <tr>
        <td id="L56" class="blob-num js-line-number" data-line-number="56"></td>
        <td id="LC56" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L57" class="blob-num js-line-number" data-line-number="57"></td>
        <td id="LC57" class="blob-code blob-code-inner js-file-line"><span class="pl-k">UNION ALL</span></td>
      </tr>
      <tr>
        <td id="L58" class="blob-num js-line-number" data-line-number="58"></td>
        <td id="LC58" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span> all tourism</span></td>
      </tr>
      <tr>
        <td id="L59" class="blob-num js-line-number" data-line-number="59"></td>
        <td id="LC59" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> osm_id,<span class="pl-s"><span class="pl-pds">&#39;</span>point<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> origin_geometry, access,<span class="pl-s"><span class="pl-pds">&quot;</span>addr:housenumber<span class="pl-pds">&quot;</span></span> <span class="pl-k">as</span> housenumber, tourism, shop, </td>
      </tr>
      <tr>
        <td id="L60" class="blob-num js-line-number" data-line-number="60"></td>
        <td id="LC60" class="blob-code blob-code-inner js-file-line">tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>origin<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin, tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>organic<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> organic, denomination,brand,name,</td>
      </tr>
      <tr>
        <td id="L61" class="blob-num js-line-number" data-line-number="61"></td>
        <td id="LC61" class="blob-code blob-code-inner js-file-line">operator,public_transport,railway,religion,tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>opening_hours<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> opening_hours, ref,tags, way <span class="pl-k">as</span> geom, tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> wheelchair  </td>
      </tr>
      <tr>
        <td id="L62" class="blob-num js-line-number" data-line-number="62"></td>
        <td id="LC62" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> planet_osm_point</td>
      </tr>
      <tr>
        <td id="L63" class="blob-num js-line-number" data-line-number="63"></td>
        <td id="LC63" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> tourism <span class="pl-k">IS NOT NULL</span></td>
      </tr>
      <tr>
        <td id="L64" class="blob-num js-line-number" data-line-number="64"></td>
        <td id="LC64" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L65" class="blob-num js-line-number" data-line-number="65"></td>
        <td id="LC65" class="blob-code blob-code-inner js-file-line"><span class="pl-k">UNION ALL</span></td>
      </tr>
      <tr>
        <td id="L66" class="blob-num js-line-number" data-line-number="66"></td>
        <td id="LC66" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L67" class="blob-num js-line-number" data-line-number="67"></td>
        <td id="LC67" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span> all sports (sport stuff is usually not tagged with amenity, but with leisure=* and sport=*)</span></td>
      </tr>
      <tr>
        <td id="L68" class="blob-num js-line-number" data-line-number="68"></td>
        <td id="LC68" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L69" class="blob-num js-line-number" data-line-number="69"></td>
        <td id="LC69" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> osm_id,<span class="pl-s"><span class="pl-pds">&#39;</span>point<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> origin_geometry, access,<span class="pl-s"><span class="pl-pds">&quot;</span>addr:housenumber<span class="pl-pds">&quot;</span></span> <span class="pl-k">as</span> housenumber, <span class="pl-s"><span class="pl-pds">&#39;</span>sport<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> amenity, shop, </td>
      </tr>
      <tr>
        <td id="L70" class="blob-num js-line-number" data-line-number="70"></td>
        <td id="LC70" class="blob-code blob-code-inner js-file-line">tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>origin<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin, tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>organic<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> organic, denomination,brand,name,</td>
      </tr>
      <tr>
        <td id="L71" class="blob-num js-line-number" data-line-number="71"></td>
        <td id="LC71" class="blob-code blob-code-inner js-file-line">operator,public_transport,railway,religion,tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>opening_hours<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> opening_hours, ref, tags<span class="pl-k">||</span>hstore(<span class="pl-s"><span class="pl-pds">&#39;</span>sport<span class="pl-pds">&#39;</span></span>, sport)<span class="pl-k">||</span>hstore(<span class="pl-s"><span class="pl-pds">&#39;</span>leisure<span class="pl-pds">&#39;</span></span>, leisure)  <span class="pl-k">AS</span> tags, way <span class="pl-k">as</span> geom,</td>
      </tr>
      <tr>
        <td id="L72" class="blob-num js-line-number" data-line-number="72"></td>
        <td id="LC72" class="blob-code blob-code-inner js-file-line">tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> wheelchair  </td>
      </tr>
      <tr>
        <td id="L73" class="blob-num js-line-number" data-line-number="73"></td>
        <td id="LC73" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> planet_osm_point</td>
      </tr>
      <tr>
        <td id="L74" class="blob-num js-line-number" data-line-number="74"></td>
        <td id="LC74" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> (sport <span class="pl-k">IS NOT NULL</span></td>
      </tr>
      <tr>
        <td id="L75" class="blob-num js-line-number" data-line-number="75"></td>
        <td id="LC75" class="blob-code blob-code-inner js-file-line"><span class="pl-k">OR</span> leisure <span class="pl-k">=</span> any (<span class="pl-k">SELECT</span> (jsonb_array_elements_text((select_from_variable_container_o(<span class="pl-s"><span class="pl-pds">&#39;</span>amenity_config<span class="pl-pds">&#39;</span></span>)<span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>leisure<span class="pl-pds">&#39;</span></span><span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>add<span class="pl-pds">&#39;</span></span>)::jsonb))))</td>
      </tr>
      <tr>
        <td id="L76" class="blob-num js-line-number" data-line-number="76"></td>
        <td id="LC76" class="blob-code blob-code-inner js-file-line"><span class="pl-k">AND</span> leisure <span class="pl-k">!=</span>(<span class="pl-k">SELECT</span> (jsonb_array_elements_text((select_from_variable_container_o(<span class="pl-s"><span class="pl-pds">&#39;</span>amenity_config<span class="pl-pds">&#39;</span></span>)<span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>leisure<span class="pl-pds">&#39;</span></span><span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>discard<span class="pl-pds">&#39;</span></span>)::jsonb)))</td>
      </tr>
      <tr>
        <td id="L77" class="blob-num js-line-number" data-line-number="77"></td>
        <td id="LC77" class="blob-code blob-code-inner js-file-line"><span class="pl-k">AND</span> sport <span class="pl-k">!=</span>(<span class="pl-k">SELECT</span> (jsonb_array_elements_text((select_from_variable_container_o(<span class="pl-s"><span class="pl-pds">&#39;</span>amenity_config<span class="pl-pds">&#39;</span></span>)<span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>sport<span class="pl-pds">&#39;</span></span><span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>discard<span class="pl-pds">&#39;</span></span>)::jsonb)))</td>
      </tr>
      <tr>
        <td id="L78" class="blob-num js-line-number" data-line-number="78"></td>
        <td id="LC78" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L79" class="blob-num js-line-number" data-line-number="79"></td>
        <td id="LC79" class="blob-code blob-code-inner js-file-line"><span class="pl-k">UNION ALL</span></td>
      </tr>
      <tr>
        <td id="L80" class="blob-num js-line-number" data-line-number="80"></td>
        <td id="LC80" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L81" class="blob-num js-line-number" data-line-number="81"></td>
        <td id="LC81" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> osm_id,<span class="pl-s"><span class="pl-pds">&#39;</span>polygon<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> origin_geometry, access,<span class="pl-s"><span class="pl-pds">&quot;</span>addr:housenumber<span class="pl-pds">&quot;</span></span> <span class="pl-k">as</span> housenumber, <span class="pl-s"><span class="pl-pds">&#39;</span>sport<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> amenity, shop, </td>
      </tr>
      <tr>
        <td id="L82" class="blob-num js-line-number" data-line-number="82"></td>
        <td id="LC82" class="blob-code blob-code-inner js-file-line">tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>origin<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin, tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>organic<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> organic, denomination,brand,name,</td>
      </tr>
      <tr>
        <td id="L83" class="blob-num js-line-number" data-line-number="83"></td>
        <td id="LC83" class="blob-code blob-code-inner js-file-line">operator,public_transport,railway,religion,tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>opening_hours<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> opening_hours, ref, tags<span class="pl-k">||</span>hstore(<span class="pl-s"><span class="pl-pds">&#39;</span>sport<span class="pl-pds">&#39;</span></span>, sport)<span class="pl-k">||</span>hstore(<span class="pl-s"><span class="pl-pds">&#39;</span>leisure<span class="pl-pds">&#39;</span></span>, leisure)  <span class="pl-k">AS</span> tags, st_centroid(way) <span class="pl-k">as</span> geom,</td>
      </tr>
      <tr>
        <td id="L84" class="blob-num js-line-number" data-line-number="84"></td>
        <td id="LC84" class="blob-code blob-code-inner js-file-line">tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> wheelchair  </td>
      </tr>
      <tr>
        <td id="L85" class="blob-num js-line-number" data-line-number="85"></td>
        <td id="LC85" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> planet_osm_polygon</td>
      </tr>
      <tr>
        <td id="L86" class="blob-num js-line-number" data-line-number="86"></td>
        <td id="LC86" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> (sport <span class="pl-k">IS NOT NULL</span></td>
      </tr>
      <tr>
        <td id="L87" class="blob-num js-line-number" data-line-number="87"></td>
        <td id="LC87" class="blob-code blob-code-inner js-file-line"><span class="pl-k">OR</span> leisure <span class="pl-k">=</span> any (<span class="pl-k">SELECT</span> (jsonb_array_elements_text((select_from_variable_container_o(<span class="pl-s"><span class="pl-pds">&#39;</span>amenity_config<span class="pl-pds">&#39;</span></span>)<span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>leisure<span class="pl-pds">&#39;</span></span><span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>add<span class="pl-pds">&#39;</span></span>)::jsonb))))</td>
      </tr>
      <tr>
        <td id="L88" class="blob-num js-line-number" data-line-number="88"></td>
        <td id="LC88" class="blob-code blob-code-inner js-file-line"><span class="pl-k">AND</span> leisure <span class="pl-k">!=</span>(<span class="pl-k">SELECT</span> (jsonb_array_elements_text((select_from_variable_container_o(<span class="pl-s"><span class="pl-pds">&#39;</span>amenity_config<span class="pl-pds">&#39;</span></span>)<span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>leisure<span class="pl-pds">&#39;</span></span><span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>discard<span class="pl-pds">&#39;</span></span>)::jsonb)))</td>
      </tr>
      <tr>
        <td id="L89" class="blob-num js-line-number" data-line-number="89"></td>
        <td id="LC89" class="blob-code blob-code-inner js-file-line"><span class="pl-k">AND</span> sport <span class="pl-k">!=</span>(<span class="pl-k">SELECT</span> (jsonb_array_elements_text((select_from_variable_container_o(<span class="pl-s"><span class="pl-pds">&#39;</span>amenity_config<span class="pl-pds">&#39;</span></span>)<span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>sport<span class="pl-pds">&#39;</span></span><span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>discard<span class="pl-pds">&#39;</span></span>)::jsonb)))</td>
      </tr>
      <tr>
        <td id="L90" class="blob-num js-line-number" data-line-number="90"></td>
        <td id="LC90" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L91" class="blob-num js-line-number" data-line-number="91"></td>
        <td id="LC91" class="blob-code blob-code-inner js-file-line"><span class="pl-k">UNION ALL</span> </td>
      </tr>
      <tr>
        <td id="L92" class="blob-num js-line-number" data-line-number="92"></td>
        <td id="LC92" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L93" class="blob-num js-line-number" data-line-number="93"></td>
        <td id="LC93" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span> Add fitness centers</span></td>
      </tr>
      <tr>
        <td id="L94" class="blob-num js-line-number" data-line-number="94"></td>
        <td id="LC94" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> osm_id,<span class="pl-s"><span class="pl-pds">&#39;</span>point<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> origin_geometry, access,<span class="pl-s"><span class="pl-pds">&quot;</span>addr:housenumber<span class="pl-pds">&quot;</span></span> <span class="pl-k">as</span> housenumber, <span class="pl-s"><span class="pl-pds">&#39;</span>gym<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> amenity, shop, </td>
      </tr>
      <tr>
        <td id="L95" class="blob-num js-line-number" data-line-number="95"></td>
        <td id="LC95" class="blob-code blob-code-inner js-file-line">tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>origin<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin, tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>organic<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> organic, denomination,brand,name,</td>
      </tr>
      <tr>
        <td id="L96" class="blob-num js-line-number" data-line-number="96"></td>
        <td id="LC96" class="blob-code blob-code-inner js-file-line">operator,public_transport,railway,religion,tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>opening_hours<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> opening_hours, ref, tags<span class="pl-k">||</span>hstore(<span class="pl-s"><span class="pl-pds">&#39;</span>sport<span class="pl-pds">&#39;</span></span>, sport)<span class="pl-k">||</span>hstore(<span class="pl-s"><span class="pl-pds">&#39;</span>leisure<span class="pl-pds">&#39;</span></span>, leisure)  <span class="pl-k">AS</span> tags, way <span class="pl-k">as</span> geom,</td>
      </tr>
      <tr>
        <td id="L97" class="blob-num js-line-number" data-line-number="97"></td>
        <td id="LC97" class="blob-code blob-code-inner js-file-line">tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> wheelchair  </td>
      </tr>
      <tr>
        <td id="L98" class="blob-num js-line-number" data-line-number="98"></td>
        <td id="LC98" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> planet_osm_point </td>
      </tr>
      <tr>
        <td id="L99" class="blob-num js-line-number" data-line-number="99"></td>
        <td id="LC99" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> (leisure <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>fitness_centre<span class="pl-pds">&#39;</span></span> <span class="pl-k">OR</span> (leisure <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>sports_centre<span class="pl-pds">&#39;</span></span> <span class="pl-k">AND</span> sport <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>fitness<span class="pl-pds">&#39;</span></span>))</td>
      </tr>
      <tr>
        <td id="L100" class="blob-num js-line-number" data-line-number="100"></td>
        <td id="LC100" class="blob-code blob-code-inner js-file-line"><span class="pl-k">AND</span> (sport <span class="pl-k">IN</span>(<span class="pl-s"><span class="pl-pds">&#39;</span>multi<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>fitness<span class="pl-pds">&#39;</span></span>) <span class="pl-k">OR</span> sport IS <span class="pl-k">NULL</span>)</td>
      </tr>
      <tr>
        <td id="L101" class="blob-num js-line-number" data-line-number="101"></td>
        <td id="LC101" class="blob-code blob-code-inner js-file-line"><span class="pl-k">AND</span> NOT (<span class="pl-c1">lower</span>(name) <span class="pl-k">LIKE</span> <span class="pl-s"><span class="pl-pds">&#39;</span>%yoga%<span class="pl-pds">&#39;</span></span>)</td>
      </tr>
      <tr>
        <td id="L102" class="blob-num js-line-number" data-line-number="102"></td>
        <td id="LC102" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L103" class="blob-num js-line-number" data-line-number="103"></td>
        <td id="LC103" class="blob-code blob-code-inner js-file-line"><span class="pl-k">UNION ALL</span> </td>
      </tr>
      <tr>
        <td id="L104" class="blob-num js-line-number" data-line-number="104"></td>
        <td id="LC104" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L105" class="blob-num js-line-number" data-line-number="105"></td>
        <td id="LC105" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> osm_id,<span class="pl-s"><span class="pl-pds">&#39;</span>polygon<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> origin_geometry, access,<span class="pl-s"><span class="pl-pds">&quot;</span>addr:housenumber<span class="pl-pds">&quot;</span></span> <span class="pl-k">as</span> housenumber, <span class="pl-s"><span class="pl-pds">&#39;</span>gym<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> amenity, shop, </td>
      </tr>
      <tr>
        <td id="L106" class="blob-num js-line-number" data-line-number="106"></td>
        <td id="LC106" class="blob-code blob-code-inner js-file-line">tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>origin<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin, tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>organic<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> organic, denomination,brand,name,</td>
      </tr>
      <tr>
        <td id="L107" class="blob-num js-line-number" data-line-number="107"></td>
        <td id="LC107" class="blob-code blob-code-inner js-file-line">operator,public_transport,railway,religion,tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>opening_hours<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> opening_hours, ref, tags<span class="pl-k">||</span>hstore(<span class="pl-s"><span class="pl-pds">&#39;</span>sport<span class="pl-pds">&#39;</span></span>, sport)<span class="pl-k">||</span>hstore(<span class="pl-s"><span class="pl-pds">&#39;</span>leisure<span class="pl-pds">&#39;</span></span>, leisure)  <span class="pl-k">AS</span> tags, ST_Centroid(way) <span class="pl-k">as</span> geom,</td>
      </tr>
      <tr>
        <td id="L108" class="blob-num js-line-number" data-line-number="108"></td>
        <td id="LC108" class="blob-code blob-code-inner js-file-line">tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> wheelchair  </td>
      </tr>
      <tr>
        <td id="L109" class="blob-num js-line-number" data-line-number="109"></td>
        <td id="LC109" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> planet_osm_polygon</td>
      </tr>
      <tr>
        <td id="L110" class="blob-num js-line-number" data-line-number="110"></td>
        <td id="LC110" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> (leisure <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>fitness_centre<span class="pl-pds">&#39;</span></span> <span class="pl-k">OR</span> (leisure <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>sports_centre<span class="pl-pds">&#39;</span></span> <span class="pl-k">AND</span> sport <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>fitness<span class="pl-pds">&#39;</span></span>))</td>
      </tr>
      <tr>
        <td id="L111" class="blob-num js-line-number" data-line-number="111"></td>
        <td id="LC111" class="blob-code blob-code-inner js-file-line"><span class="pl-k">AND</span> (sport <span class="pl-k">IN</span>(<span class="pl-s"><span class="pl-pds">&#39;</span>multi<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>fitness<span class="pl-pds">&#39;</span></span>) <span class="pl-k">OR</span> sport IS <span class="pl-k">NULL</span>)</td>
      </tr>
      <tr>
        <td id="L112" class="blob-num js-line-number" data-line-number="112"></td>
        <td id="LC112" class="blob-code blob-code-inner js-file-line"><span class="pl-k">AND</span> NOT (<span class="pl-c1">lower</span>(name) <span class="pl-k">LIKE</span> <span class="pl-s"><span class="pl-pds">&#39;</span>%yoga%<span class="pl-pds">&#39;</span></span>)</td>
      </tr>
      <tr>
        <td id="L113" class="blob-num js-line-number" data-line-number="113"></td>
        <td id="LC113" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L114" class="blob-num js-line-number" data-line-number="114"></td>
        <td id="LC114" class="blob-code blob-code-inner js-file-line"><span class="pl-k">UNION ALL</span> </td>
      </tr>
      <tr>
        <td id="L115" class="blob-num js-line-number" data-line-number="115"></td>
        <td id="LC115" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span> Add Yoga centers</span></td>
      </tr>
      <tr>
        <td id="L116" class="blob-num js-line-number" data-line-number="116"></td>
        <td id="LC116" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L117" class="blob-num js-line-number" data-line-number="117"></td>
        <td id="LC117" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> osm_id,<span class="pl-s"><span class="pl-pds">&#39;</span>point<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> origin_geometry, access,<span class="pl-s"><span class="pl-pds">&quot;</span>addr:housenumber<span class="pl-pds">&quot;</span></span> <span class="pl-k">as</span> housenumber, <span class="pl-s"><span class="pl-pds">&#39;</span>yoga<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> amenity, shop, </td>
      </tr>
      <tr>
        <td id="L118" class="blob-num js-line-number" data-line-number="118"></td>
        <td id="LC118" class="blob-code blob-code-inner js-file-line">tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>origin<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin, tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>organic<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> organic, denomination,brand,name,</td>
      </tr>
      <tr>
        <td id="L119" class="blob-num js-line-number" data-line-number="119"></td>
        <td id="LC119" class="blob-code blob-code-inner js-file-line">operator,public_transport,railway,religion,tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>opening_hours<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> opening_hours, ref, tags<span class="pl-k">||</span>hstore(<span class="pl-s"><span class="pl-pds">&#39;</span>sport<span class="pl-pds">&#39;</span></span>, sport)<span class="pl-k">||</span>hstore(<span class="pl-s"><span class="pl-pds">&#39;</span>leisure<span class="pl-pds">&#39;</span></span>, leisure)  <span class="pl-k">AS</span> tags, way <span class="pl-k">as</span> geom,</td>
      </tr>
      <tr>
        <td id="L120" class="blob-num js-line-number" data-line-number="120"></td>
        <td id="LC120" class="blob-code blob-code-inner js-file-line">tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> wheelchair</td>
      </tr>
      <tr>
        <td id="L121" class="blob-num js-line-number" data-line-number="121"></td>
        <td id="LC121" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> planet_osm_point <span class="pl-k">WHERE</span> (sport <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>yoga<span class="pl-pds">&#39;</span></span> <span class="pl-k">OR</span> <span class="pl-c1">lower</span>(name) <span class="pl-k">LIKE</span> <span class="pl-s"><span class="pl-pds">&#39;</span>%yoga%<span class="pl-pds">&#39;</span></span>) <span class="pl-k">AND</span> shop IS <span class="pl-k">NULL</span></td>
      </tr>
      <tr>
        <td id="L122" class="blob-num js-line-number" data-line-number="122"></td>
        <td id="LC122" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L123" class="blob-num js-line-number" data-line-number="123"></td>
        <td id="LC123" class="blob-code blob-code-inner js-file-line"><span class="pl-k">UNION ALL</span> </td>
      </tr>
      <tr>
        <td id="L124" class="blob-num js-line-number" data-line-number="124"></td>
        <td id="LC124" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L125" class="blob-num js-line-number" data-line-number="125"></td>
        <td id="LC125" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span>-----------------------------------------------------------------</span></td>
      </tr>
      <tr>
        <td id="L126" class="blob-num js-line-number" data-line-number="126"></td>
        <td id="LC126" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span>------------------School polygons--------------------------------</span></td>
      </tr>
      <tr>
        <td id="L127" class="blob-num js-line-number" data-line-number="127"></td>
        <td id="LC127" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span>-----------------------------------------------------------------</span></td>
      </tr>
      <tr>
        <td id="L128" class="blob-num js-line-number" data-line-number="128"></td>
        <td id="LC128" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L129" class="blob-num js-line-number" data-line-number="129"></td>
        <td id="LC129" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span>------------------------primary_school (über Name, wenn kein isced:level)------------------</span></td>
      </tr>
      <tr>
        <td id="L130" class="blob-num js-line-number" data-line-number="130"></td>
        <td id="LC130" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> osm_id, <span class="pl-s"><span class="pl-pds">&#39;</span>polygon<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> origin_geometry, access,<span class="pl-s"><span class="pl-pds">&quot;</span>addr:housenumber<span class="pl-pds">&quot;</span></span> <span class="pl-k">as</span> housenumber, <span class="pl-s"><span class="pl-pds">&#39;</span>primary_school<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> amenity, shop, </td>
      </tr>
      <tr>
        <td id="L131" class="blob-num js-line-number" data-line-number="131"></td>
        <td id="LC131" class="blob-code blob-code-inner js-file-line">tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>origin<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin, tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>organic<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> organic, denomination,brand,name,</td>
      </tr>
      <tr>
        <td id="L132" class="blob-num js-line-number" data-line-number="132"></td>
        <td id="LC132" class="blob-code blob-code-inner js-file-line">operator,public_transport,railway,religion,tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>opening_hours<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> opening_hours, ref,tags, st_centroid(way) <span class="pl-k">as</span> geom,</td>
      </tr>
      <tr>
        <td id="L133" class="blob-num js-line-number" data-line-number="133"></td>
        <td id="LC133" class="blob-code blob-code-inner js-file-line">tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> wheelchair  </td>
      </tr>
      <tr>
        <td id="L134" class="blob-num js-line-number" data-line-number="134"></td>
        <td id="LC134" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> planet_osm_polygon</td>
      </tr>
      <tr>
        <td id="L135" class="blob-num js-line-number" data-line-number="135"></td>
        <td id="LC135" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> amenity <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>school<span class="pl-pds">&#39;</span></span> <span class="pl-k">AND</span> (</td>
      </tr>
      <tr>
        <td id="L136" class="blob-num js-line-number" data-line-number="136"></td>
        <td id="LC136" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">lower</span>(name) <span class="pl-k">LIKE</span> ANY (<span class="pl-k">SELECT</span> (jsonb_array_elements_text((select_from_variable_container_o(<span class="pl-s"><span class="pl-pds">&#39;</span>amenity_config<span class="pl-pds">&#39;</span></span>)<span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>primary_school<span class="pl-pds">&#39;</span></span><span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>add<span class="pl-pds">&#39;</span></span>)::jsonb))) <span class="pl-k">AND</span></td>
      </tr>
      <tr>
        <td id="L137" class="blob-num js-line-number" data-line-number="137"></td>
        <td id="LC137" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">lower</span>(name) NOT <span class="pl-k">LIKE</span> ANY (<span class="pl-k">SELECT</span> (jsonb_array_elements_text((select_from_variable_container_o(<span class="pl-s"><span class="pl-pds">&#39;</span>amenity_config<span class="pl-pds">&#39;</span></span>)<span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>primary_school<span class="pl-pds">&#39;</span></span><span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>discard<span class="pl-pds">&#39;</span></span>)::jsonb)))</td>
      </tr>
      <tr>
        <td id="L138" class="blob-num js-line-number" data-line-number="138"></td>
        <td id="LC138" class="blob-code blob-code-inner js-file-line"><span class="pl-k">AND</span> tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>isced:level<span class="pl-pds">&#39;</span></span> IS <span class="pl-k">NULL</span>)</td>
      </tr>
      <tr>
        <td id="L139" class="blob-num js-line-number" data-line-number="139"></td>
        <td id="LC139" class="blob-code blob-code-inner js-file-line"><span class="pl-k">OR</span> tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>isced:level<span class="pl-pds">&#39;</span></span> <span class="pl-k">LIKE</span> <span class="pl-s"><span class="pl-pds">&#39;</span>%1%<span class="pl-pds">&#39;</span></span></td>
      </tr>
      <tr>
        <td id="L140" class="blob-num js-line-number" data-line-number="140"></td>
        <td id="LC140" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L141" class="blob-num js-line-number" data-line-number="141"></td>
        <td id="LC141" class="blob-code blob-code-inner js-file-line"><span class="pl-k">UNION ALL</span></td>
      </tr>
      <tr>
        <td id="L142" class="blob-num js-line-number" data-line-number="142"></td>
        <td id="LC142" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L143" class="blob-num js-line-number" data-line-number="143"></td>
        <td id="LC143" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L144" class="blob-num js-line-number" data-line-number="144"></td>
        <td id="LC144" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span>------------secondary_school; Haupt-/Mittel-/Realschule/Gymnasium (über Name, wenn kein isced:level)----------------</span></td>
      </tr>
      <tr>
        <td id="L145" class="blob-num js-line-number" data-line-number="145"></td>
        <td id="LC145" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L146" class="blob-num js-line-number" data-line-number="146"></td>
        <td id="LC146" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> osm_id, <span class="pl-s"><span class="pl-pds">&#39;</span>polygon<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> origin_geometry, access,<span class="pl-s"><span class="pl-pds">&quot;</span>addr:housenumber<span class="pl-pds">&quot;</span></span> <span class="pl-k">as</span> housenumber, <span class="pl-s"><span class="pl-pds">&#39;</span>secondary_school<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> amenity, shop, </td>
      </tr>
      <tr>
        <td id="L147" class="blob-num js-line-number" data-line-number="147"></td>
        <td id="LC147" class="blob-code blob-code-inner js-file-line">tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>origin<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin, tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>organic<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> organic, denomination,brand,name,</td>
      </tr>
      <tr>
        <td id="L148" class="blob-num js-line-number" data-line-number="148"></td>
        <td id="LC148" class="blob-code blob-code-inner js-file-line">operator,public_transport,railway,religion,tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>opening_hours<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> opening_hours, ref,tags, st_centroid(way) <span class="pl-k">as</span> geom,</td>
      </tr>
      <tr>
        <td id="L149" class="blob-num js-line-number" data-line-number="149"></td>
        <td id="LC149" class="blob-code blob-code-inner js-file-line">tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> wheelchair  </td>
      </tr>
      <tr>
        <td id="L150" class="blob-num js-line-number" data-line-number="150"></td>
        <td id="LC150" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> planet_osm_polygon</td>
      </tr>
      <tr>
        <td id="L151" class="blob-num js-line-number" data-line-number="151"></td>
        <td id="LC151" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> amenity <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>school<span class="pl-pds">&#39;</span></span> <span class="pl-k">AND</span> ((</td>
      </tr>
      <tr>
        <td id="L152" class="blob-num js-line-number" data-line-number="152"></td>
        <td id="LC152" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">lower</span>(name) <span class="pl-k">LIKE</span> ANY (<span class="pl-k">SELECT</span> (jsonb_array_elements_text((select_from_variable_container_o(<span class="pl-s"><span class="pl-pds">&#39;</span>amenity_config<span class="pl-pds">&#39;</span></span>)<span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>secondary_school<span class="pl-pds">&#39;</span></span><span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>add<span class="pl-pds">&#39;</span></span>)::jsonb)))</td>
      </tr>
      <tr>
        <td id="L153" class="blob-num js-line-number" data-line-number="153"></td>
        <td id="LC153" class="blob-code blob-code-inner js-file-line"><span class="pl-k">AND</span></td>
      </tr>
      <tr>
        <td id="L154" class="blob-num js-line-number" data-line-number="154"></td>
        <td id="LC154" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">lower</span>(name) NOT <span class="pl-k">LIKE</span> ANY (<span class="pl-k">SELECT</span> (jsonb_array_elements_text((select_from_variable_container_o(<span class="pl-s"><span class="pl-pds">&#39;</span>amenity_config<span class="pl-pds">&#39;</span></span>)<span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>secondary_school<span class="pl-pds">&#39;</span></span><span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>discard<span class="pl-pds">&#39;</span></span>)::jsonb)))</td>
      </tr>
      <tr>
        <td id="L155" class="blob-num js-line-number" data-line-number="155"></td>
        <td id="LC155" class="blob-code blob-code-inner js-file-line"><span class="pl-k">AND</span> tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>isced:level<span class="pl-pds">&#39;</span></span> IS <span class="pl-k">NULL</span></td>
      </tr>
      <tr>
        <td id="L156" class="blob-num js-line-number" data-line-number="156"></td>
        <td id="LC156" class="blob-code blob-code-inner js-file-line">)</td>
      </tr>
      <tr>
        <td id="L157" class="blob-num js-line-number" data-line-number="157"></td>
        <td id="LC157" class="blob-code blob-code-inner js-file-line"><span class="pl-k">OR</span> tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>isced:level<span class="pl-pds">&#39;</span></span> <span class="pl-k">LIKE</span> ANY (ARRAY[<span class="pl-s"><span class="pl-pds">&#39;</span>%2%<span class="pl-pds">&#39;</span></span>, <span class="pl-s"><span class="pl-pds">&#39;</span>%3%<span class="pl-pds">&#39;</span></span>])</td>
      </tr>
      <tr>
        <td id="L158" class="blob-num js-line-number" data-line-number="158"></td>
        <td id="LC158" class="blob-code blob-code-inner js-file-line">)</td>
      </tr>
      <tr>
        <td id="L159" class="blob-num js-line-number" data-line-number="159"></td>
        <td id="LC159" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L160" class="blob-num js-line-number" data-line-number="160"></td>
        <td id="LC160" class="blob-code blob-code-inner js-file-line"><span class="pl-k">UNION ALL</span> </td>
      </tr>
      <tr>
        <td id="L161" class="blob-num js-line-number" data-line-number="161"></td>
        <td id="LC161" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L162" class="blob-num js-line-number" data-line-number="162"></td>
        <td id="LC162" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span>---------------------------------------------------------------</span></td>
      </tr>
      <tr>
        <td id="L163" class="blob-num js-line-number" data-line-number="163"></td>
        <td id="LC163" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span>------------------School points--------------------------------</span></td>
      </tr>
      <tr>
        <td id="L164" class="blob-num js-line-number" data-line-number="164"></td>
        <td id="LC164" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span>---------------------------------------------------------------</span></td>
      </tr>
      <tr>
        <td id="L165" class="blob-num js-line-number" data-line-number="165"></td>
        <td id="LC165" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L166" class="blob-num js-line-number" data-line-number="166"></td>
        <td id="LC166" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span>------------------------primary_school (über Name, wenn kein isced:level)------------------</span></td>
      </tr>
      <tr>
        <td id="L167" class="blob-num js-line-number" data-line-number="167"></td>
        <td id="LC167" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L168" class="blob-num js-line-number" data-line-number="168"></td>
        <td id="LC168" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> osm_id, <span class="pl-s"><span class="pl-pds">&#39;</span>point<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> origin_geometry, access,<span class="pl-s"><span class="pl-pds">&quot;</span>addr:housenumber<span class="pl-pds">&quot;</span></span> <span class="pl-k">as</span> housenumber, <span class="pl-s"><span class="pl-pds">&#39;</span>primary_school<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> amenity, shop, </td>
      </tr>
      <tr>
        <td id="L169" class="blob-num js-line-number" data-line-number="169"></td>
        <td id="LC169" class="blob-code blob-code-inner js-file-line">tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>origin<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin, tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>organic<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> organic, denomination,brand,name,</td>
      </tr>
      <tr>
        <td id="L170" class="blob-num js-line-number" data-line-number="170"></td>
        <td id="LC170" class="blob-code blob-code-inner js-file-line">operator,public_transport,railway,religion,tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>opening_hours<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> opening_hours, ref,tags, st_centroid(way) <span class="pl-k">as</span> geom,</td>
      </tr>
      <tr>
        <td id="L171" class="blob-num js-line-number" data-line-number="171"></td>
        <td id="LC171" class="blob-code blob-code-inner js-file-line">tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> wheelchair  </td>
      </tr>
      <tr>
        <td id="L172" class="blob-num js-line-number" data-line-number="172"></td>
        <td id="LC172" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> planet_osm_point</td>
      </tr>
      <tr>
        <td id="L173" class="blob-num js-line-number" data-line-number="173"></td>
        <td id="LC173" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> amenity <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>school<span class="pl-pds">&#39;</span></span> <span class="pl-k">AND</span> (</td>
      </tr>
      <tr>
        <td id="L174" class="blob-num js-line-number" data-line-number="174"></td>
        <td id="LC174" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">lower</span>(name) <span class="pl-k">LIKE</span> ANY (<span class="pl-k">SELECT</span> (jsonb_array_elements_text((select_from_variable_container_o(<span class="pl-s"><span class="pl-pds">&#39;</span>amenity_config<span class="pl-pds">&#39;</span></span>)<span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>primary_school<span class="pl-pds">&#39;</span></span><span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>add<span class="pl-pds">&#39;</span></span>)::jsonb))) <span class="pl-k">AND</span></td>
      </tr>
      <tr>
        <td id="L175" class="blob-num js-line-number" data-line-number="175"></td>
        <td id="LC175" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">lower</span>(name) NOT <span class="pl-k">LIKE</span> ANY (<span class="pl-k">SELECT</span> (jsonb_array_elements_text((select_from_variable_container_o(<span class="pl-s"><span class="pl-pds">&#39;</span>amenity_config<span class="pl-pds">&#39;</span></span>)<span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>primary_school<span class="pl-pds">&#39;</span></span><span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>discard<span class="pl-pds">&#39;</span></span>)::jsonb)))</td>
      </tr>
      <tr>
        <td id="L176" class="blob-num js-line-number" data-line-number="176"></td>
        <td id="LC176" class="blob-code blob-code-inner js-file-line"><span class="pl-k">AND</span> tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>isced:level<span class="pl-pds">&#39;</span></span> IS <span class="pl-k">NULL</span>)</td>
      </tr>
      <tr>
        <td id="L177" class="blob-num js-line-number" data-line-number="177"></td>
        <td id="LC177" class="blob-code blob-code-inner js-file-line"><span class="pl-k">OR</span> tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>isced:level<span class="pl-pds">&#39;</span></span> <span class="pl-k">LIKE</span> <span class="pl-s"><span class="pl-pds">&#39;</span>%1%<span class="pl-pds">&#39;</span></span></td>
      </tr>
      <tr>
        <td id="L178" class="blob-num js-line-number" data-line-number="178"></td>
        <td id="LC178" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L179" class="blob-num js-line-number" data-line-number="179"></td>
        <td id="LC179" class="blob-code blob-code-inner js-file-line"><span class="pl-k">UNION ALL</span></td>
      </tr>
      <tr>
        <td id="L180" class="blob-num js-line-number" data-line-number="180"></td>
        <td id="LC180" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L181" class="blob-num js-line-number" data-line-number="181"></td>
        <td id="LC181" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span>------------secondary_school; Haupt-/Mittel-/Realschule/Gymnasium (über Name, wenn kein isced:level)----------------</span></td>
      </tr>
      <tr>
        <td id="L182" class="blob-num js-line-number" data-line-number="182"></td>
        <td id="LC182" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L183" class="blob-num js-line-number" data-line-number="183"></td>
        <td id="LC183" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> osm_id, <span class="pl-s"><span class="pl-pds">&#39;</span>point<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> origin_geometry, access,<span class="pl-s"><span class="pl-pds">&quot;</span>addr:housenumber<span class="pl-pds">&quot;</span></span> <span class="pl-k">as</span> housenumber, <span class="pl-s"><span class="pl-pds">&#39;</span>secondary_school<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> amenity, shop, </td>
      </tr>
      <tr>
        <td id="L184" class="blob-num js-line-number" data-line-number="184"></td>
        <td id="LC184" class="blob-code blob-code-inner js-file-line">tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>origin<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin, tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>organic<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> organic, denomination,brand,name,</td>
      </tr>
      <tr>
        <td id="L185" class="blob-num js-line-number" data-line-number="185"></td>
        <td id="LC185" class="blob-code blob-code-inner js-file-line">operator,public_transport,railway,religion,tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>opening_hours<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> opening_hours, ref,tags, st_centroid(way) <span class="pl-k">as</span> geom,</td>
      </tr>
      <tr>
        <td id="L186" class="blob-num js-line-number" data-line-number="186"></td>
        <td id="LC186" class="blob-code blob-code-inner js-file-line">tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> wheelchair  </td>
      </tr>
      <tr>
        <td id="L187" class="blob-num js-line-number" data-line-number="187"></td>
        <td id="LC187" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> planet_osm_point</td>
      </tr>
      <tr>
        <td id="L188" class="blob-num js-line-number" data-line-number="188"></td>
        <td id="LC188" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> amenity <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>school<span class="pl-pds">&#39;</span></span> <span class="pl-k">AND</span> ((</td>
      </tr>
      <tr>
        <td id="L189" class="blob-num js-line-number" data-line-number="189"></td>
        <td id="LC189" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">lower</span>(name) <span class="pl-k">LIKE</span> ANY (<span class="pl-k">SELECT</span> (jsonb_array_elements_text((select_from_variable_container_o(<span class="pl-s"><span class="pl-pds">&#39;</span>amenity_config<span class="pl-pds">&#39;</span></span>)<span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>secondary_school<span class="pl-pds">&#39;</span></span><span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>add<span class="pl-pds">&#39;</span></span>)::jsonb)))</td>
      </tr>
      <tr>
        <td id="L190" class="blob-num js-line-number" data-line-number="190"></td>
        <td id="LC190" class="blob-code blob-code-inner js-file-line"><span class="pl-k">AND</span></td>
      </tr>
      <tr>
        <td id="L191" class="blob-num js-line-number" data-line-number="191"></td>
        <td id="LC191" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">lower</span>(name) NOT <span class="pl-k">LIKE</span> ANY (<span class="pl-k">SELECT</span> (jsonb_array_elements_text((select_from_variable_container_o(<span class="pl-s"><span class="pl-pds">&#39;</span>amenity_config<span class="pl-pds">&#39;</span></span>)<span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>secondary_school<span class="pl-pds">&#39;</span></span><span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>discard<span class="pl-pds">&#39;</span></span>)::jsonb)))</td>
      </tr>
      <tr>
        <td id="L192" class="blob-num js-line-number" data-line-number="192"></td>
        <td id="LC192" class="blob-code blob-code-inner js-file-line"><span class="pl-k">AND</span> tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>isced:level<span class="pl-pds">&#39;</span></span> IS <span class="pl-k">NULL</span></td>
      </tr>
      <tr>
        <td id="L193" class="blob-num js-line-number" data-line-number="193"></td>
        <td id="LC193" class="blob-code blob-code-inner js-file-line">)</td>
      </tr>
      <tr>
        <td id="L194" class="blob-num js-line-number" data-line-number="194"></td>
        <td id="LC194" class="blob-code blob-code-inner js-file-line"><span class="pl-k">OR</span> tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>isced:level<span class="pl-pds">&#39;</span></span> <span class="pl-k">LIKE</span> ANY (ARRAY[<span class="pl-s"><span class="pl-pds">&#39;</span>%2%<span class="pl-pds">&#39;</span></span>, <span class="pl-s"><span class="pl-pds">&#39;</span>%3%<span class="pl-pds">&#39;</span></span>])</td>
      </tr>
      <tr>
        <td id="L195" class="blob-num js-line-number" data-line-number="195"></td>
        <td id="LC195" class="blob-code blob-code-inner js-file-line">)</td>
      </tr>
      <tr>
        <td id="L196" class="blob-num js-line-number" data-line-number="196"></td>
        <td id="LC196" class="blob-code blob-code-inner js-file-line">);</td>
      </tr>
      <tr>
        <td id="L197" class="blob-num js-line-number" data-line-number="197"></td>
        <td id="LC197" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L198" class="blob-num js-line-number" data-line-number="198"></td>
        <td id="LC198" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span>---------------------------------------------------------------</span></td>
      </tr>
      <tr>
        <td id="L199" class="blob-num js-line-number" data-line-number="199"></td>
        <td id="LC199" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span>-----------Insert kindergartens--------------------------------</span></td>
      </tr>
      <tr>
        <td id="L200" class="blob-num js-line-number" data-line-number="200"></td>
        <td id="LC200" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span>---------------------------------------------------------------</span></td>
      </tr>
      <tr>
        <td id="L201" class="blob-num js-line-number" data-line-number="201"></td>
        <td id="LC201" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L202" class="blob-num js-line-number" data-line-number="202"></td>
        <td id="LC202" class="blob-code blob-code-inner js-file-line"><span class="pl-k">DROP</span> <span class="pl-k">TABLE</span> IF EXISTS kindergartens_polygons;</td>
      </tr>
      <tr>
        <td id="L203" class="blob-num js-line-number" data-line-number="203"></td>
        <td id="LC203" class="blob-code blob-code-inner js-file-line">CREATE TEMP TABLE kindergartens_polygons <span class="pl-k">AS</span> (</td>
      </tr>
      <tr>
        <td id="L204" class="blob-num js-line-number" data-line-number="204"></td>
        <td id="LC204" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> osm_id,<span class="pl-s"><span class="pl-pds">&#39;</span>polygon<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> origin_geometry, access, <span class="pl-s"><span class="pl-pds">&quot;</span>addr:housenumber<span class="pl-pds">&quot;</span></span> <span class="pl-k">as</span> housenumber, amenity, shop, </td>
      </tr>
      <tr>
        <td id="L205" class="blob-num js-line-number" data-line-number="205"></td>
        <td id="LC205" class="blob-code blob-code-inner js-file-line">tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>origin<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin, tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>organic<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> organic, denomination, brand, name,</td>
      </tr>
      <tr>
        <td id="L206" class="blob-num js-line-number" data-line-number="206"></td>
        <td id="LC206" class="blob-code blob-code-inner js-file-line">operator, public_transport, railway, religion, tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>opening_hours<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> opening_hours, ref, tags::hstore <span class="pl-k">AS</span> tags, way <span class="pl-k">as</span> geom,</td>
      </tr>
      <tr>
        <td id="L207" class="blob-num js-line-number" data-line-number="207"></td>
        <td id="LC207" class="blob-code blob-code-inner js-file-line">tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> wheelchair, ST_centroid(way) <span class="pl-k">AS</span> centroid</td>
      </tr>
      <tr>
        <td id="L208" class="blob-num js-line-number" data-line-number="208"></td>
        <td id="LC208" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> planet_osm_polygon</td>
      </tr>
      <tr>
        <td id="L209" class="blob-num js-line-number" data-line-number="209"></td>
        <td id="LC209" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> amenity <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>kindergarten<span class="pl-pds">&#39;</span></span> );</td>
      </tr>
      <tr>
        <td id="L210" class="blob-num js-line-number" data-line-number="210"></td>
        <td id="LC210" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L211" class="blob-num js-line-number" data-line-number="211"></td>
        <td id="LC211" class="blob-code blob-code-inner js-file-line"><span class="pl-k">DROP</span> <span class="pl-k">TABLE</span> IF EXISTS kindergarten_duplicates;</td>
      </tr>
      <tr>
        <td id="L212" class="blob-num js-line-number" data-line-number="212"></td>
        <td id="LC212" class="blob-code blob-code-inner js-file-line">CREATE TEMP TABLE kindergarten_duplicates <span class="pl-k">AS</span> (</td>
      </tr>
      <tr>
        <td id="L213" class="blob-num js-line-number" data-line-number="213"></td>
        <td id="LC213" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> <span class="pl-k">*</span></td>
      </tr>
      <tr>
        <td id="L214" class="blob-num js-line-number" data-line-number="214"></td>
        <td id="LC214" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> (</td>
      </tr>
      <tr>
        <td id="L215" class="blob-num js-line-number" data-line-number="215"></td>
        <td id="LC215" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">SELECT</span> o.<span class="pl-k">*</span>, ST_Distance(<span class="pl-c1">o</span>.<span class="pl-c1">centroid</span>,<span class="pl-c1">p</span>.<span class="pl-c1">centroid</span>) <span class="pl-k">AS</span> distance</td>
      </tr>
      <tr>
        <td id="L216" class="blob-num js-line-number" data-line-number="216"></td>
        <td id="LC216" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">FROM</span> kindergartens_polygons o</td>
      </tr>
      <tr>
        <td id="L217" class="blob-num js-line-number" data-line-number="217"></td>
        <td id="LC217" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">JOIN</span> kindergartens_polygons p</td>
      </tr>
      <tr>
        <td id="L218" class="blob-num js-line-number" data-line-number="218"></td>
        <td id="LC218" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">ON</span> ST_DWithin( <span class="pl-c1">o</span>.<span class="pl-c1">centroid</span>::geography, <span class="pl-c1">p</span>.<span class="pl-c1">centroid</span>::geography, select_from_variable_container_s(<span class="pl-s"><span class="pl-pds">&#39;</span>duplicated_kindergarten_lookup_radius<span class="pl-pds">&#39;</span></span>)::float)</td>
      </tr>
      <tr>
        <td id="L219" class="blob-num js-line-number" data-line-number="219"></td>
        <td id="LC219" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">AND</span> NOT ST_DWithin(<span class="pl-c1">o</span>.<span class="pl-c1">centroid</span>, <span class="pl-c1">p</span>.<span class="pl-c1">centroid</span>, <span class="pl-c1">0</span>)</td>
      </tr>
      <tr>
        <td id="L220" class="blob-num js-line-number" data-line-number="220"></td>
        <td id="LC220" class="blob-code blob-code-inner js-file-line">	) <span class="pl-k">AS</span> duplicates) ;</td>
      </tr>
      <tr>
        <td id="L221" class="blob-num js-line-number" data-line-number="221"></td>
        <td id="LC221" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L222" class="blob-num js-line-number" data-line-number="222"></td>
        <td id="LC222" class="blob-code blob-code-inner js-file-line"><span class="pl-k">DELETE</span> <span class="pl-k">FROM</span> kindergartens_polygons <span class="pl-k">WHERE</span> osm_id <span class="pl-k">=</span> ANY (<span class="pl-k">SELECT</span> osm_id <span class="pl-k">FROM</span> kindergarten_duplicates);</td>
      </tr>
      <tr>
        <td id="L223" class="blob-num js-line-number" data-line-number="223"></td>
        <td id="LC223" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L224" class="blob-num js-line-number" data-line-number="224"></td>
        <td id="LC224" class="blob-code blob-code-inner js-file-line"><span class="pl-k">INSERT INTO</span> kindergartens_polygons </td>
      </tr>
      <tr>
        <td id="L225" class="blob-num js-line-number" data-line-number="225"></td>
        <td id="LC225" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> <span class="pl-c1">max</span>(osm_id), <span class="pl-s"><span class="pl-pds">&#39;</span>polygon<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin_geometry, <span class="pl-c1">max</span>(access) <span class="pl-k">AS</span> access, <span class="pl-c1">max</span>(housenumber) <span class="pl-k">AS</span> housenumber, </td>
      </tr>
      <tr>
        <td id="L226" class="blob-num js-line-number" data-line-number="226"></td>
        <td id="LC226" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">max</span>(amenity) <span class="pl-k">AS</span> amenity, <span class="pl-c1">max</span>(shop) <span class="pl-k">AS</span> shop, <span class="pl-c1">max</span>(tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>origin<span class="pl-pds">&#39;</span></span>) <span class="pl-k">AS</span> origin, <span class="pl-c1">max</span>(tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>organic<span class="pl-pds">&#39;</span></span>) <span class="pl-k">AS</span> organic, <span class="pl-c1">max</span>(denomination) <span class="pl-k">AS</span> denomination,</td>
      </tr>
      <tr>
        <td id="L227" class="blob-num js-line-number" data-line-number="227"></td>
        <td id="LC227" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">max</span>(brand) <span class="pl-k">AS</span> brand, <span class="pl-c1">max</span>(name) <span class="pl-k">AS</span> name, <span class="pl-c1">max</span>(operator) <span class="pl-k">AS</span> operator, <span class="pl-c1">max</span>(public_transport) <span class="pl-k">AS</span> public_transport, <span class="pl-c1">max</span>(railway) <span class="pl-k">AS</span> railway,</td>
      </tr>
      <tr>
        <td id="L228" class="blob-num js-line-number" data-line-number="228"></td>
        <td id="LC228" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">max</span>(religion) <span class="pl-k">AS</span> religion, <span class="pl-c1">max</span>(tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>opening_hours<span class="pl-pds">&#39;</span></span>) <span class="pl-k">AS</span> opening_hours, <span class="pl-c1">max</span>(REF) <span class="pl-k">AS</span> ref, <span class="pl-c1">max</span>(tags::<span class="pl-k">TEXT</span>)::hstore <span class="pl-k">AS</span> tags, <span class="pl-k">null</span>,</td>
      </tr>
      <tr>
        <td id="L229" class="blob-num js-line-number" data-line-number="229"></td>
        <td id="LC229" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">max</span>(tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span>) <span class="pl-k">AS</span> wheelchair, <span class="pl-c1">max</span>(centroid)::geometry</td>
      </tr>
      <tr>
        <td id="L230" class="blob-num js-line-number" data-line-number="230"></td>
        <td id="LC230" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> kindergarten_duplicates <span class="pl-k">GROUP BY</span> distance;</td>
      </tr>
      <tr>
        <td id="L231" class="blob-num js-line-number" data-line-number="231"></td>
        <td id="LC231" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L232" class="blob-num js-line-number" data-line-number="232"></td>
        <td id="LC232" class="blob-code blob-code-inner js-file-line"><span class="pl-k">INSERT INTO</span> pois </td>
      </tr>
      <tr>
        <td id="L233" class="blob-num js-line-number" data-line-number="233"></td>
        <td id="LC233" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT DISTINCT</span> <span class="pl-c1">p</span>.<span class="pl-c1">osm_id</span>,<span class="pl-s"><span class="pl-pds">&#39;</span>point<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> origin_geometry, <span class="pl-c1">p</span>.<span class="pl-c1">access</span>, <span class="pl-s"><span class="pl-pds">&quot;</span>addr:housenumber<span class="pl-pds">&quot;</span></span> <span class="pl-k">AS</span> housenumber, <span class="pl-c1">p</span>.<span class="pl-c1">amenity</span>, <span class="pl-c1">p</span>.<span class="pl-c1">shop</span>, <span class="pl-c"><span class="pl-c">--</span>p.&quot;addr:housenumber&quot; doesn&#39;t work</span></td>
      </tr>
      <tr>
        <td id="L234" class="blob-num js-line-number" data-line-number="234"></td>
        <td id="LC234" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">p</span>.<span class="pl-c1">tags</span> <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>origin<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin, <span class="pl-c1">p</span>.<span class="pl-c1">tags</span> <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>organic<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> organic, <span class="pl-c1">p</span>.<span class="pl-c1">denomination</span>,<span class="pl-c1">p</span>.<span class="pl-c1">brand</span>,<span class="pl-c1">p</span>.<span class="pl-c1">name</span>,</td>
      </tr>
      <tr>
        <td id="L235" class="blob-num js-line-number" data-line-number="235"></td>
        <td id="LC235" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">p</span>.<span class="pl-c1">operator</span>,<span class="pl-c1">p</span>.<span class="pl-c1">public_transport</span>,<span class="pl-c1">p</span>.<span class="pl-c1">railway</span>,<span class="pl-c1">p</span>.<span class="pl-c1">religion</span>,<span class="pl-c1">p</span>.<span class="pl-c1">tags</span> <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>opening_hours<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> opening_hours, <span class="pl-c1">p</span>.<span class="pl-c1">ref</span>, <span class="pl-c1">p</span>.<span class="pl-c1">tags</span>::hstore <span class="pl-k">AS</span> tags, <span class="pl-c1">p</span>.<span class="pl-c1">way</span> <span class="pl-k">as</span> geom,</td>
      </tr>
      <tr>
        <td id="L236" class="blob-num js-line-number" data-line-number="236"></td>
        <td id="LC236" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">p</span>.<span class="pl-c1">tags</span> <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> wheelchair </td>
      </tr>
      <tr>
        <td id="L237" class="blob-num js-line-number" data-line-number="237"></td>
        <td id="LC237" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> planet_osm_point p</td>
      </tr>
      <tr>
        <td id="L238" class="blob-num js-line-number" data-line-number="238"></td>
        <td id="LC238" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> <span class="pl-c1">p</span>.<span class="pl-c1">amenity</span> <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>kindergarten<span class="pl-pds">&#39;</span></span></td>
      </tr>
      <tr>
        <td id="L239" class="blob-num js-line-number" data-line-number="239"></td>
        <td id="LC239" class="blob-code blob-code-inner js-file-line">EXCEPT</td>
      </tr>
      <tr>
        <td id="L240" class="blob-num js-line-number" data-line-number="240"></td>
        <td id="LC240" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT DISTINCT</span> <span class="pl-c1">p</span>.<span class="pl-c1">osm_id</span>,<span class="pl-s"><span class="pl-pds">&#39;</span>point<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> origin_geometry, <span class="pl-c1">p</span>.<span class="pl-c1">access</span>, <span class="pl-s"><span class="pl-pds">&quot;</span>addr:housenumber<span class="pl-pds">&quot;</span></span> <span class="pl-k">AS</span> housenumber, <span class="pl-c1">p</span>.<span class="pl-c1">amenity</span>, <span class="pl-c1">p</span>.<span class="pl-c1">shop</span>, <span class="pl-c"><span class="pl-c">--</span>p.&quot;addr:housenumber&quot; doesn&#39;t work</span></td>
      </tr>
      <tr>
        <td id="L241" class="blob-num js-line-number" data-line-number="241"></td>
        <td id="LC241" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">p</span>.<span class="pl-c1">tags</span> <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>origin<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin, <span class="pl-c1">p</span>.<span class="pl-c1">tags</span> <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>organic<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> organic, <span class="pl-c1">p</span>.<span class="pl-c1">denomination</span>,<span class="pl-c1">p</span>.<span class="pl-c1">brand</span>,<span class="pl-c1">p</span>.<span class="pl-c1">name</span>,</td>
      </tr>
      <tr>
        <td id="L242" class="blob-num js-line-number" data-line-number="242"></td>
        <td id="LC242" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">p</span>.<span class="pl-c1">operator</span>,<span class="pl-c1">p</span>.<span class="pl-c1">public_transport</span>,<span class="pl-c1">p</span>.<span class="pl-c1">railway</span>,<span class="pl-c1">p</span>.<span class="pl-c1">religion</span>,<span class="pl-c1">p</span>.<span class="pl-c1">tags</span> <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>opening_hours<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> opening_hours, <span class="pl-c1">p</span>.<span class="pl-c1">ref</span>, <span class="pl-c1">p</span>.<span class="pl-c1">tags</span>::hstore <span class="pl-k">AS</span> tags, <span class="pl-c1">p</span>.<span class="pl-c1">way</span> <span class="pl-k">as</span> geom,</td>
      </tr>
      <tr>
        <td id="L243" class="blob-num js-line-number" data-line-number="243"></td>
        <td id="LC243" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">p</span>.<span class="pl-c1">tags</span> <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> wheelchair </td>
      </tr>
      <tr>
        <td id="L244" class="blob-num js-line-number" data-line-number="244"></td>
        <td id="LC244" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> planet_osm_point p, kindergartens_polygons kp</td>
      </tr>
      <tr>
        <td id="L245" class="blob-num js-line-number" data-line-number="245"></td>
        <td id="LC245" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> <span class="pl-c1">p</span>.<span class="pl-c1">amenity</span> <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>kindergarten<span class="pl-pds">&#39;</span></span> <span class="pl-k">AND</span> ST_Intersects(ST_Buffer(<span class="pl-c1">p</span>.<span class="pl-c1">way</span>::geography,select_from_variable_container_s(<span class="pl-s"><span class="pl-pds">&#39;</span>duplicated_kindergarten_lookup_radius<span class="pl-pds">&#39;</span></span>)::float ), <span class="pl-c1">kp</span>.<span class="pl-c1">geom</span>)</td>
      </tr>
      <tr>
        <td id="L246" class="blob-num js-line-number" data-line-number="246"></td>
        <td id="LC246" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L247" class="blob-num js-line-number" data-line-number="247"></td>
        <td id="LC247" class="blob-code blob-code-inner js-file-line"><span class="pl-k">UNION ALL</span> </td>
      </tr>
      <tr>
        <td id="L248" class="blob-num js-line-number" data-line-number="248"></td>
        <td id="LC248" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L249" class="blob-num js-line-number" data-line-number="249"></td>
        <td id="LC249" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> <span class="pl-c1">kp</span>.<span class="pl-c1">osm_id</span>, <span class="pl-c1">kp</span>.<span class="pl-c1">origin_geometry</span>, <span class="pl-c1">kp</span>.<span class="pl-c1">ACCESS</span>, <span class="pl-c1">kp</span>.<span class="pl-c1">housenumber</span>, <span class="pl-c1">kp</span>.<span class="pl-c1">amenity</span>, <span class="pl-c1">kp</span>.<span class="pl-c1">shop</span>, <span class="pl-c1">kp</span>.<span class="pl-c1">origin</span>, <span class="pl-c1">kp</span>.<span class="pl-c1">organic</span>, <span class="pl-c1">kp</span>.<span class="pl-c1">denomination</span>, <span class="pl-c1">kp</span>.<span class="pl-c1">brand</span>, <span class="pl-c1">kp</span>.<span class="pl-c1">name</span>, </td>
      </tr>
      <tr>
        <td id="L250" class="blob-num js-line-number" data-line-number="250"></td>
        <td id="LC250" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">kp</span>.<span class="pl-c1">OPERATOR</span>, <span class="pl-c1">kp</span>.<span class="pl-c1">public_transport</span>, <span class="pl-c1">kp</span>.<span class="pl-c1">railway</span>, <span class="pl-c1">kp</span>.<span class="pl-c1">religion</span>, <span class="pl-c1">kp</span>.<span class="pl-c1">opening_hours</span>, <span class="pl-c1">kp</span>.<span class="pl-c1">REF</span>, <span class="pl-c1">kp</span>.<span class="pl-c1">tags</span>, <span class="pl-c1">kp</span>.<span class="pl-c1">centroid</span> <span class="pl-k">AS</span> geom, <span class="pl-c1">kp</span>.<span class="pl-c1">wheelchair</span></td>
      </tr>
      <tr>
        <td id="L251" class="blob-num js-line-number" data-line-number="251"></td>
        <td id="LC251" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> kindergartens_polygons kp;</td>
      </tr>
      <tr>
        <td id="L252" class="blob-num js-line-number" data-line-number="252"></td>
        <td id="LC252" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L253" class="blob-num js-line-number" data-line-number="253"></td>
        <td id="LC253" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span> Insert outdoor fitness stations</span></td>
      </tr>
      <tr>
        <td id="L254" class="blob-num js-line-number" data-line-number="254"></td>
        <td id="LC254" class="blob-code blob-code-inner js-file-line"><span class="pl-k">DROP</span> <span class="pl-k">TABLE</span> IF EXISTS containing_polygons;</td>
      </tr>
      <tr>
        <td id="L255" class="blob-num js-line-number" data-line-number="255"></td>
        <td id="LC255" class="blob-code blob-code-inner js-file-line">CREATE TEMP TABLE containing_polygons (geom geometry);</td>
      </tr>
      <tr>
        <td id="L256" class="blob-num js-line-number" data-line-number="256"></td>
        <td id="LC256" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L257" class="blob-num js-line-number" data-line-number="257"></td>
        <td id="LC257" class="blob-code blob-code-inner js-file-line"><span class="pl-k">INSERT INTO</span> containing_polygons</td>
      </tr>
      <tr>
        <td id="L258" class="blob-num js-line-number" data-line-number="258"></td>
        <td id="LC258" class="blob-code blob-code-inner js-file-line">WITH merged_geom <span class="pl-k">AS</span> (</td>
      </tr>
      <tr>
        <td id="L259" class="blob-num js-line-number" data-line-number="259"></td>
        <td id="LC259" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> (ST_Dump(way)).geom <span class="pl-k">AS</span> geom</td>
      </tr>
      <tr>
        <td id="L260" class="blob-num js-line-number" data-line-number="260"></td>
        <td id="LC260" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> (</td>
      </tr>
      <tr>
        <td id="L261" class="blob-num js-line-number" data-line-number="261"></td>
        <td id="LC261" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">SELECT</span> ST_Union(way) <span class="pl-k">AS</span> way		</td>
      </tr>
      <tr>
        <td id="L262" class="blob-num js-line-number" data-line-number="262"></td>
        <td id="LC262" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">FROM</span> planet_osm_polygon</td>
      </tr>
      <tr>
        <td id="L263" class="blob-num js-line-number" data-line-number="263"></td>
        <td id="LC263" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">WHERE</span> leisure <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>fitness_station<span class="pl-pds">&#39;</span></span> <span class="pl-k">OR</span>(<span class="pl-s"><span class="pl-pds">&quot;</span>leisure<span class="pl-pds">&quot;</span></span> <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>pitch<span class="pl-pds">&#39;</span></span> <span class="pl-k">and</span> <span class="pl-s"><span class="pl-pds">&quot;</span>sport<span class="pl-pds">&quot;</span></span> <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>fitness<span class="pl-pds">&#39;</span></span>))x)</td>
      </tr>
      <tr>
        <td id="L264" class="blob-num js-line-number" data-line-number="264"></td>
        <td id="LC264" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> <span class="pl-c1">m</span>.<span class="pl-c1">geom</span> <span class="pl-k">FROM</span> planet_osm_polygon pop, merged_geom m <span class="pl-k">GROUP BY</span> <span class="pl-c1">m</span>.<span class="pl-c1">geom</span>;</td>
      </tr>
      <tr>
        <td id="L265" class="blob-num js-line-number" data-line-number="265"></td>
        <td id="LC265" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L266" class="blob-num js-line-number" data-line-number="266"></td>
        <td id="LC266" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span> Paste zones attributes in containing polygons</span></td>
      </tr>
      <tr>
        <td id="L267" class="blob-num js-line-number" data-line-number="267"></td>
        <td id="LC267" class="blob-code blob-code-inner js-file-line"><span class="pl-k">DROP</span> <span class="pl-k">TABLE</span> IF EXISTS grouping_polygons;</td>
      </tr>
      <tr>
        <td id="L268" class="blob-num js-line-number" data-line-number="268"></td>
        <td id="LC268" class="blob-code blob-code-inner js-file-line">CREATE TEMP TABLE grouping_polygons  (<span class="pl-k">LIKE</span> planet_osm_polygon INCLUDING INDEXES);</td>
      </tr>
      <tr>
        <td id="L269" class="blob-num js-line-number" data-line-number="269"></td>
        <td id="LC269" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L270" class="blob-num js-line-number" data-line-number="270"></td>
        <td id="LC270" class="blob-code blob-code-inner js-file-line"><span class="pl-k">INSERT INTO</span> grouping_polygons</td>
      </tr>
      <tr>
        <td id="L271" class="blob-num js-line-number" data-line-number="271"></td>
        <td id="LC271" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> pop.<span class="pl-k">*</span> <span class="pl-k">FROM</span> containing_polygons</td>
      </tr>
      <tr>
        <td id="L272" class="blob-num js-line-number" data-line-number="272"></td>
        <td id="LC272" class="blob-code blob-code-inner js-file-line"><span class="pl-k">LEFT JOIN</span> planet_osm_polygon pop </td>
      </tr>
      <tr>
        <td id="L273" class="blob-num js-line-number" data-line-number="273"></td>
        <td id="LC273" class="blob-code blob-code-inner js-file-line"><span class="pl-k">ON</span> ST_Contains(<span class="pl-c1">pop</span>.<span class="pl-c1">way</span>, geom)</td>
      </tr>
      <tr>
        <td id="L274" class="blob-num js-line-number" data-line-number="274"></td>
        <td id="LC274" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> <span class="pl-c1">pop</span>.<span class="pl-c1">leisure</span> <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>fitness_station<span class="pl-pds">&#39;</span></span> <span class="pl-k">OR</span>(<span class="pl-s"><span class="pl-pds">&quot;</span>leisure<span class="pl-pds">&quot;</span></span> <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>pitch<span class="pl-pds">&#39;</span></span> <span class="pl-k">and</span> <span class="pl-s"><span class="pl-pds">&quot;</span>sport<span class="pl-pds">&quot;</span></span> <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>fitness<span class="pl-pds">&#39;</span></span>);</td>
      </tr>
      <tr>
        <td id="L275" class="blob-num js-line-number" data-line-number="275"></td>
        <td id="LC275" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L276" class="blob-num js-line-number" data-line-number="276"></td>
        <td id="LC276" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span> Select points that are into polygons</span></td>
      </tr>
      <tr>
        <td id="L277" class="blob-num js-line-number" data-line-number="277"></td>
        <td id="LC277" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L278" class="blob-num js-line-number" data-line-number="278"></td>
        <td id="LC278" class="blob-code blob-code-inner js-file-line"><span class="pl-k">DROP</span> <span class="pl-k">TABLE</span> IF EXISTS fitness_points;</td>
      </tr>
      <tr>
        <td id="L279" class="blob-num js-line-number" data-line-number="279"></td>
        <td id="LC279" class="blob-code blob-code-inner js-file-line">CREATE TEMP TABLE fitness_points (<span class="pl-k">LIKE</span> planet_osm_point INCLUDING ALL);</td>
      </tr>
      <tr>
        <td id="L280" class="blob-num js-line-number" data-line-number="280"></td>
        <td id="LC280" class="blob-code blob-code-inner js-file-line"><span class="pl-k">INSERT INTO</span> fitness_points(</td>
      </tr>
      <tr>
        <td id="L281" class="blob-num js-line-number" data-line-number="281"></td>
        <td id="LC281" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT DISTINCT</span> pop.<span class="pl-k">*</span> <span class="pl-k">FROM</span> planet_osm_point pop</td>
      </tr>
      <tr>
        <td id="L282" class="blob-num js-line-number" data-line-number="282"></td>
        <td id="LC282" class="blob-code blob-code-inner js-file-line"><span class="pl-k">LEFT JOIN</span> grouping_polygons gp</td>
      </tr>
      <tr>
        <td id="L283" class="blob-num js-line-number" data-line-number="283"></td>
        <td id="LC283" class="blob-code blob-code-inner js-file-line"><span class="pl-k">ON</span> ST_intersects(<span class="pl-c1">pop</span>.<span class="pl-c1">way</span>, <span class="pl-c1">gp</span>.<span class="pl-c1">way</span>)</td>
      </tr>
      <tr>
        <td id="L284" class="blob-num js-line-number" data-line-number="284"></td>
        <td id="LC284" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> <span class="pl-c1">pop</span>.<span class="pl-c1">leisure</span> <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>fitness_station<span class="pl-pds">&#39;</span></span> <span class="pl-k">AND</span> ST_contains(<span class="pl-c1">gp</span>.<span class="pl-c1">way</span>,<span class="pl-c1">pop</span>.<span class="pl-c1">way</span>)</td>
      </tr>
      <tr>
        <td id="L285" class="blob-num js-line-number" data-line-number="285"></td>
        <td id="LC285" class="blob-code blob-code-inner js-file-line">);</td>
      </tr>
      <tr>
        <td id="L286" class="blob-num js-line-number" data-line-number="286"></td>
        <td id="LC286" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L287" class="blob-num js-line-number" data-line-number="287"></td>
        <td id="LC287" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span>- ADD to pois</span></td>
      </tr>
      <tr>
        <td id="L288" class="blob-num js-line-number" data-line-number="288"></td>
        <td id="LC288" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L289" class="blob-num js-line-number" data-line-number="289"></td>
        <td id="LC289" class="blob-code blob-code-inner js-file-line"><span class="pl-k">INSERT INTO</span> pois(</td>
      </tr>
      <tr>
        <td id="L290" class="blob-num js-line-number" data-line-number="290"></td>
        <td id="LC290" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L291" class="blob-num js-line-number" data-line-number="291"></td>
        <td id="LC291" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> <span class="pl-c1">pop</span>.<span class="pl-c1">osm_id</span>, <span class="pl-s"><span class="pl-pds">&#39;</span>polygon<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin_geometry, <span class="pl-c1">pop</span>.<span class="pl-c1">ACCESS</span> <span class="pl-k">AS</span> ACCESS, pop.<span class="pl-s"><span class="pl-pds">&quot;</span>addr:housenumber<span class="pl-pds">&quot;</span></span> <span class="pl-k">AS</span> <span class="pl-s"><span class="pl-pds">&quot;</span>addr:housenumber<span class="pl-pds">&quot;</span></span>,</td>
      </tr>
      <tr>
        <td id="L292" class="blob-num js-line-number" data-line-number="292"></td>
        <td id="LC292" class="blob-code blob-code-inner js-file-line"><span class="pl-s"><span class="pl-pds">&#39;</span>outdoor_fitness_station<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> amenity, <span class="pl-c1">pop</span>.<span class="pl-c1">shop</span> <span class="pl-k">AS</span> store, <span class="pl-c1">pop</span>.<span class="pl-c1">tags</span><span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>origin<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin, <span class="pl-c1">pop</span>.<span class="pl-c1">tags</span><span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>organic<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> organic, <span class="pl-c1">pop</span>.<span class="pl-c1">denomination</span> <span class="pl-k">AS</span> denomination,</td>
      </tr>
      <tr>
        <td id="L293" class="blob-num js-line-number" data-line-number="293"></td>
        <td id="LC293" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">pop</span>.<span class="pl-c1">brand</span> <span class="pl-k">AS</span> brand, <span class="pl-c1">gp</span>.<span class="pl-c1">name</span> <span class="pl-k">AS</span> name, <span class="pl-c1">pop</span>.<span class="pl-c1">OPERATOR</span> <span class="pl-k">AS</span> operator, <span class="pl-c1">pop</span>.<span class="pl-c1">public_transport</span> <span class="pl-k">AS</span> public_transport, <span class="pl-c1">pop</span>.<span class="pl-c1">railway</span> <span class="pl-k">AS</span> railway,</td>
      </tr>
      <tr>
        <td id="L294" class="blob-num js-line-number" data-line-number="294"></td>
        <td id="LC294" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">pop</span>.<span class="pl-c1">religion</span> <span class="pl-k">AS</span> religion, <span class="pl-c1">pop</span>.<span class="pl-c1">tags</span><span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>opening_hours<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> opening_hours, <span class="pl-c1">pop</span>.<span class="pl-c1">ref</span> <span class="pl-k">AS</span> ref, (<span class="pl-c1">pop</span>.<span class="pl-c1">tags</span><span class="pl-k">||</span>hstore(<span class="pl-s"><span class="pl-pds">&#39;</span>sport<span class="pl-pds">&#39;</span></span>, <span class="pl-c1">pop</span>.<span class="pl-c1">sport</span>)<span class="pl-k">||</span>hstore(<span class="pl-s"><span class="pl-pds">&#39;</span>leisure<span class="pl-pds">&#39;</span></span>, <span class="pl-c1">pop</span>.<span class="pl-c1">leisure</span>))::hstore  <span class="pl-k">AS</span> tags, ST_Centroid(<span class="pl-c1">pop</span>.<span class="pl-c1">way</span>) <span class="pl-k">AS</span> geom, <span class="pl-c1">pop</span>.<span class="pl-c1">tags</span> <span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> wheelchair</td>
      </tr>
      <tr>
        <td id="L295" class="blob-num js-line-number" data-line-number="295"></td>
        <td id="LC295" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> planet_osm_polygon pop</td>
      </tr>
      <tr>
        <td id="L296" class="blob-num js-line-number" data-line-number="296"></td>
        <td id="LC296" class="blob-code blob-code-inner js-file-line"><span class="pl-k">LEFT JOIN</span> grouping_polygons gp</td>
      </tr>
      <tr>
        <td id="L297" class="blob-num js-line-number" data-line-number="297"></td>
        <td id="LC297" class="blob-code blob-code-inner js-file-line"><span class="pl-k">ON</span> ST_intersects(<span class="pl-c1">pop</span>.<span class="pl-c1">way</span>, <span class="pl-c1">gp</span>.<span class="pl-c1">way</span>)</td>
      </tr>
      <tr>
        <td id="L298" class="blob-num js-line-number" data-line-number="298"></td>
        <td id="LC298" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> <span class="pl-c1">pop</span>.<span class="pl-c1">leisure</span> <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>fitness_station<span class="pl-pds">&#39;</span></span>  <span class="pl-k">OR</span>(<span class="pl-c1">pop</span>.<span class="pl-c1">leisure</span> <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>pitch<span class="pl-pds">&#39;</span></span> <span class="pl-k">and</span> <span class="pl-c1">pop</span>.<span class="pl-c1">sport</span> <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>fitness<span class="pl-pds">&#39;</span></span>)</td>
      </tr>
      <tr>
        <td id="L299" class="blob-num js-line-number" data-line-number="299"></td>
        <td id="LC299" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span>WHERE pop.leisure = &#39;fitness_station&#39; AND NOT ST_contains(pop.way, gp.way)</span></td>
      </tr>
      <tr>
        <td id="L300" class="blob-num js-line-number" data-line-number="300"></td>
        <td id="LC300" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L301" class="blob-num js-line-number" data-line-number="301"></td>
        <td id="LC301" class="blob-code blob-code-inner js-file-line"><span class="pl-k">UNION ALL</span> </td>
      </tr>
      <tr>
        <td id="L302" class="blob-num js-line-number" data-line-number="302"></td>
        <td id="LC302" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L303" class="blob-num js-line-number" data-line-number="303"></td>
        <td id="LC303" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> osm_id, <span class="pl-s"><span class="pl-pds">&#39;</span>point<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin_geometry, ACCESS <span class="pl-k">AS</span> ACCESS, <span class="pl-s"><span class="pl-pds">&quot;</span>addr:housenumber<span class="pl-pds">&quot;</span></span> <span class="pl-k">AS</span> <span class="pl-s"><span class="pl-pds">&quot;</span>addr:housenumber<span class="pl-pds">&quot;</span></span>,</td>
      </tr>
      <tr>
        <td id="L304" class="blob-num js-line-number" data-line-number="304"></td>
        <td id="LC304" class="blob-code blob-code-inner js-file-line"><span class="pl-s"><span class="pl-pds">&#39;</span>outdoor_fitness_station<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> amenity, shop <span class="pl-k">AS</span> store, tags<span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>origin<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin, tags<span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>organic<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> organic, denomination <span class="pl-k">AS</span> denomination,</td>
      </tr>
      <tr>
        <td id="L305" class="blob-num js-line-number" data-line-number="305"></td>
        <td id="LC305" class="blob-code blob-code-inner js-file-line">brand <span class="pl-k">AS</span> brand, name <span class="pl-k">AS</span> name, OPERATOR <span class="pl-k">AS</span> operator, public_transport <span class="pl-k">AS</span> public_transport, railway <span class="pl-k">AS</span> railway,</td>
      </tr>
      <tr>
        <td id="L306" class="blob-num js-line-number" data-line-number="306"></td>
        <td id="LC306" class="blob-code blob-code-inner js-file-line">religion <span class="pl-k">AS</span> religion, tags<span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>opening_hours<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> opening_hours, ref <span class="pl-k">AS</span> ref, (tags<span class="pl-k">||</span>hstore(<span class="pl-s"><span class="pl-pds">&#39;</span>sport<span class="pl-pds">&#39;</span></span>, sport)<span class="pl-k">||</span>hstore(<span class="pl-s"><span class="pl-pds">&#39;</span>leisure<span class="pl-pds">&#39;</span></span>, leisure))::hstore, way <span class="pl-k">AS</span> geom, tags <span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> wheelchair</td>
      </tr>
      <tr>
        <td id="L307" class="blob-num js-line-number" data-line-number="307"></td>
        <td id="LC307" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> fitness_points</td>
      </tr>
      <tr>
        <td id="L308" class="blob-num js-line-number" data-line-number="308"></td>
        <td id="LC308" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L309" class="blob-num js-line-number" data-line-number="309"></td>
        <td id="LC309" class="blob-code blob-code-inner js-file-line"><span class="pl-k">UNION ALL</span></td>
      </tr>
      <tr>
        <td id="L310" class="blob-num js-line-number" data-line-number="310"></td>
        <td id="LC310" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L311" class="blob-num js-line-number" data-line-number="311"></td>
        <td id="LC311" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> <span class="pl-c1">pop</span>.<span class="pl-c1">osm_id</span>, <span class="pl-s"><span class="pl-pds">&#39;</span>point<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin_geometry, <span class="pl-c1">pop</span>.<span class="pl-c1">ACCESS</span> <span class="pl-k">AS</span> ACCESS, pop.<span class="pl-s"><span class="pl-pds">&quot;</span>addr:housenumber<span class="pl-pds">&quot;</span></span> <span class="pl-k">AS</span> <span class="pl-s"><span class="pl-pds">&quot;</span>addr:housenumber<span class="pl-pds">&quot;</span></span>,</td>
      </tr>
      <tr>
        <td id="L312" class="blob-num js-line-number" data-line-number="312"></td>
        <td id="LC312" class="blob-code blob-code-inner js-file-line"><span class="pl-s"><span class="pl-pds">&#39;</span>outdoor_fitness_station<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> amenity, <span class="pl-c1">pop</span>.<span class="pl-c1">shop</span> <span class="pl-k">AS</span> store, <span class="pl-c1">pop</span>.<span class="pl-c1">tags</span><span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>origin<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin, <span class="pl-c1">pop</span>.<span class="pl-c1">tags</span><span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>organic<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> organic, <span class="pl-c1">pop</span>.<span class="pl-c1">denomination</span> <span class="pl-k">AS</span> denomination,</td>
      </tr>
      <tr>
        <td id="L313" class="blob-num js-line-number" data-line-number="313"></td>
        <td id="LC313" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">pop</span>.<span class="pl-c1">brand</span> <span class="pl-k">AS</span> brand, <span class="pl-c1">pop</span>.<span class="pl-c1">name</span> <span class="pl-k">AS</span> name, <span class="pl-c1">pop</span>.<span class="pl-c1">OPERATOR</span> <span class="pl-k">AS</span> operator, <span class="pl-c1">pop</span>.<span class="pl-c1">public_transport</span> <span class="pl-k">AS</span> public_transport, <span class="pl-c1">pop</span>.<span class="pl-c1">railway</span> <span class="pl-k">AS</span> railway,</td>
      </tr>
      <tr>
        <td id="L314" class="blob-num js-line-number" data-line-number="314"></td>
        <td id="LC314" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">pop</span>.<span class="pl-c1">religion</span> <span class="pl-k">AS</span> religion, <span class="pl-c1">pop</span>.<span class="pl-c1">tags</span><span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>opening_hours<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> opening_hours, <span class="pl-c1">pop</span>.<span class="pl-c1">ref</span> <span class="pl-k">AS</span> ref, (<span class="pl-c1">pop</span>.<span class="pl-c1">tags</span><span class="pl-k">||</span>hstore(<span class="pl-s"><span class="pl-pds">&#39;</span>sport<span class="pl-pds">&#39;</span></span>, <span class="pl-c1">pop</span>.<span class="pl-c1">sport</span>)<span class="pl-k">||</span>hstore(<span class="pl-s"><span class="pl-pds">&#39;</span>leisure<span class="pl-pds">&#39;</span></span>, <span class="pl-c1">pop</span>.<span class="pl-c1">leisure</span>))::hstore, <span class="pl-c1">pop</span>.<span class="pl-c1">way</span> <span class="pl-k">AS</span> geom, <span class="pl-c1">pop</span>.<span class="pl-c1">tags</span> <span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> wheelchair</td>
      </tr>
      <tr>
        <td id="L315" class="blob-num js-line-number" data-line-number="315"></td>
        <td id="LC315" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> planet_osm_point pop, fitness_points fp</td>
      </tr>
      <tr>
        <td id="L316" class="blob-num js-line-number" data-line-number="316"></td>
        <td id="LC316" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> <span class="pl-c1">pop</span>.<span class="pl-c1">leisure</span> <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>fitness_station<span class="pl-pds">&#39;</span></span> EXCEPT </td>
      </tr>
      <tr>
        <td id="L317" class="blob-num js-line-number" data-line-number="317"></td>
        <td id="LC317" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> <span class="pl-c1">pop</span>.<span class="pl-c1">osm_id</span>, <span class="pl-s"><span class="pl-pds">&#39;</span>point<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin_geometry, <span class="pl-c1">pop</span>.<span class="pl-c1">ACCESS</span> <span class="pl-k">AS</span> ACCESS, pop.<span class="pl-s"><span class="pl-pds">&quot;</span>addr:housenumber<span class="pl-pds">&quot;</span></span> <span class="pl-k">AS</span> <span class="pl-s"><span class="pl-pds">&quot;</span>addr:housenumber<span class="pl-pds">&quot;</span></span>,</td>
      </tr>
      <tr>
        <td id="L318" class="blob-num js-line-number" data-line-number="318"></td>
        <td id="LC318" class="blob-code blob-code-inner js-file-line"><span class="pl-s"><span class="pl-pds">&#39;</span>outdoor_fitness_station<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> amenity, <span class="pl-c1">pop</span>.<span class="pl-c1">shop</span> <span class="pl-k">AS</span> store, <span class="pl-c1">pop</span>.<span class="pl-c1">tags</span><span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>origin<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> origin, <span class="pl-c1">pop</span>.<span class="pl-c1">tags</span><span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>organic<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> organic, <span class="pl-c1">pop</span>.<span class="pl-c1">denomination</span> <span class="pl-k">AS</span> denomination,</td>
      </tr>
      <tr>
        <td id="L319" class="blob-num js-line-number" data-line-number="319"></td>
        <td id="LC319" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">pop</span>.<span class="pl-c1">brand</span> <span class="pl-k">AS</span> brand, <span class="pl-c1">pop</span>.<span class="pl-c1">name</span> <span class="pl-k">AS</span> name, <span class="pl-c1">pop</span>.<span class="pl-c1">OPERATOR</span> <span class="pl-k">AS</span> operator, <span class="pl-c1">pop</span>.<span class="pl-c1">public_transport</span> <span class="pl-k">AS</span> public_transport, <span class="pl-c1">pop</span>.<span class="pl-c1">railway</span> <span class="pl-k">AS</span> railway,</td>
      </tr>
      <tr>
        <td id="L320" class="blob-num js-line-number" data-line-number="320"></td>
        <td id="LC320" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">pop</span>.<span class="pl-c1">religion</span> <span class="pl-k">AS</span> religion, <span class="pl-c1">pop</span>.<span class="pl-c1">tags</span><span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>opening_hours<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> opening_hours, <span class="pl-c1">pop</span>.<span class="pl-c1">ref</span> <span class="pl-k">AS</span> ref, (<span class="pl-c1">pop</span>.<span class="pl-c1">tags</span><span class="pl-k">||</span>hstore(<span class="pl-s"><span class="pl-pds">&#39;</span>sport<span class="pl-pds">&#39;</span></span>, <span class="pl-c1">pop</span>.<span class="pl-c1">sport</span>)<span class="pl-k">||</span>hstore(<span class="pl-s"><span class="pl-pds">&#39;</span>leisure<span class="pl-pds">&#39;</span></span>, <span class="pl-c1">pop</span>.<span class="pl-c1">leisure</span>))::hstore, <span class="pl-c1">pop</span>.<span class="pl-c1">way</span> <span class="pl-k">AS</span> geom, <span class="pl-c1">pop</span>.<span class="pl-c1">tags</span> <span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> wheelchair</td>
      </tr>
      <tr>
        <td id="L321" class="blob-num js-line-number" data-line-number="321"></td>
        <td id="LC321" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> planet_osm_point pop, fitness_points fp</td>
      </tr>
      <tr>
        <td id="L322" class="blob-num js-line-number" data-line-number="322"></td>
        <td id="LC322" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> <span class="pl-c1">pop</span>.<span class="pl-c1">leisure</span> <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>fitness_station<span class="pl-pds">&#39;</span></span> <span class="pl-k">AND</span> ST_contains(<span class="pl-c1">pop</span>.<span class="pl-c1">way</span>, <span class="pl-c1">fp</span>.<span class="pl-c1">way</span>)</td>
      </tr>
      <tr>
        <td id="L323" class="blob-num js-line-number" data-line-number="323"></td>
        <td id="LC323" class="blob-code blob-code-inner js-file-line">  </td>
      </tr>
      <tr>
        <td id="L324" class="blob-num js-line-number" data-line-number="324"></td>
        <td id="LC324" class="blob-code blob-code-inner js-file-line">);</td>
      </tr>
      <tr>
        <td id="L325" class="blob-num js-line-number" data-line-number="325"></td>
        <td id="LC325" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L326" class="blob-num js-line-number" data-line-number="326"></td>
        <td id="LC326" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span>Distinguish kindergarten - nursery</span></td>
      </tr>
      <tr>
        <td id="L327" class="blob-num js-line-number" data-line-number="327"></td>
        <td id="LC327" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> pois_reclassification_array(<span class="pl-s"><span class="pl-pds">&#39;</span>name<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>kindergarten<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>amenity<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>nursery<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>left<span class="pl-pds">&#39;</span></span>);</td>
      </tr>
      <tr>
        <td id="L328" class="blob-num js-line-number" data-line-number="328"></td>
        <td id="LC328" class="blob-code blob-code-inner js-file-line"><span class="pl-k">UPDATE</span> pois p <span class="pl-k">SET</span> amenity <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>nursery<span class="pl-pds">&#39;</span></span></td>
      </tr>
      <tr>
        <td id="L329" class="blob-num js-line-number" data-line-number="329"></td>
        <td id="LC329" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> amenity <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>kindergarten<span class="pl-pds">&#39;</span></span>	</td>
      </tr>
      <tr>
        <td id="L330" class="blob-num js-line-number" data-line-number="330"></td>
        <td id="LC330" class="blob-code blob-code-inner js-file-line"><span class="pl-k">AND</span> (tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>max_age<span class="pl-pds">&#39;</span></span>) <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>3<span class="pl-pds">&#39;</span></span>;</td>
      </tr>
      <tr>
        <td id="L331" class="blob-num js-line-number" data-line-number="331"></td>
        <td id="LC331" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L332" class="blob-num js-line-number" data-line-number="332"></td>
        <td id="LC332" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">/*</span>End<span class="pl-c">*/</span></span></td>
      </tr>
      <tr>
        <td id="L333" class="blob-num js-line-number" data-line-number="333"></td>
        <td id="LC333" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span>----------------------------------------end kindergarten-------------------------------------------</span></td>
      </tr>
      <tr>
        <td id="L334" class="blob-num js-line-number" data-line-number="334"></td>
        <td id="LC334" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L335" class="blob-num js-line-number" data-line-number="335"></td>
        <td id="LC335" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span>For Munich grocery == convencience</span></td>
      </tr>
      <tr>
        <td id="L336" class="blob-num js-line-number" data-line-number="336"></td>
        <td id="LC336" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L337" class="blob-num js-line-number" data-line-number="337"></td>
        <td id="LC337" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> pois_reclassification(<span class="pl-s"><span class="pl-pds">&#39;</span>shop<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>grocery<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>amenity<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>convenience<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>singlevalue<span class="pl-pds">&#39;</span></span>);</td>
      </tr>
      <tr>
        <td id="L338" class="blob-num js-line-number" data-line-number="338"></td>
        <td id="LC338" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> pois_reclassification(<span class="pl-s"><span class="pl-pds">&#39;</span>shop<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>fashion<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>amenity<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>clothes<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>singlevalue<span class="pl-pds">&#39;</span></span>);</td>
      </tr>
      <tr>
        <td id="L339" class="blob-num js-line-number" data-line-number="339"></td>
        <td id="LC339" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L340" class="blob-num js-line-number" data-line-number="340"></td>
        <td id="LC340" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">/*</span>End<span class="pl-c">*/</span></span></td>
      </tr>
      <tr>
        <td id="L341" class="blob-num js-line-number" data-line-number="341"></td>
        <td id="LC341" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L342" class="blob-num js-line-number" data-line-number="342"></td>
        <td id="LC342" class="blob-code blob-code-inner js-file-line"><span class="pl-k">ALTER</span> <span class="pl-k">TABLE</span> pois add column gid <span class="pl-k">serial</span>;</td>
      </tr>
      <tr>
        <td id="L343" class="blob-num js-line-number" data-line-number="343"></td>
        <td id="LC343" class="blob-code blob-code-inner js-file-line"><span class="pl-k">ALTER</span> <span class="pl-k">TABLE</span> pois add <span class="pl-k">primary key</span>(gid); </td>
      </tr>
      <tr>
        <td id="L344" class="blob-num js-line-number" data-line-number="344"></td>
        <td id="LC344" class="blob-code blob-code-inner js-file-line"><span class="pl-k">CREATE</span> <span class="pl-k">INDEX</span> <span class="pl-en">index_pois</span> <span class="pl-k">ON</span> pois USING GIST (geom);</td>
      </tr>
      <tr>
        <td id="L345" class="blob-num js-line-number" data-line-number="345"></td>
        <td id="LC345" class="blob-code blob-code-inner js-file-line"><span class="pl-k">CREATE</span> <span class="pl-k">INDEX</span> <span class="pl-en">ON</span> pois(amenity);</td>
      </tr>
      <tr>
        <td id="L346" class="blob-num js-line-number" data-line-number="346"></td>
        <td id="LC346" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L347" class="blob-num js-line-number" data-line-number="347"></td>
        <td id="LC347" class="blob-code blob-code-inner js-file-line"><span class="pl-k">UPDATE</span> pois <span class="pl-k">SET</span> amenity <span class="pl-k">=</span> shop</td>
      </tr>
      <tr>
        <td id="L348" class="blob-num js-line-number" data-line-number="348"></td>
        <td id="LC348" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> shop <span class="pl-k">IS NOT NULL</span>;</td>
      </tr>
      <tr>
        <td id="L349" class="blob-num js-line-number" data-line-number="349"></td>
        <td id="LC349" class="blob-code blob-code-inner js-file-line"><span class="pl-k">ALTER</span> <span class="pl-k">TABLE</span> pois DROP COLUMN shop;</td>
      </tr>
      <tr>
        <td id="L350" class="blob-num js-line-number" data-line-number="350"></td>
        <td id="LC350" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L351" class="blob-num js-line-number" data-line-number="351"></td>
        <td id="LC351" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span>Refinement Shopping</span></td>
      </tr>
      <tr>
        <td id="L352" class="blob-num js-line-number" data-line-number="352"></td>
        <td id="LC352" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L353" class="blob-num js-line-number" data-line-number="353"></td>
        <td id="LC353" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> pois_reclassification_array(<span class="pl-s"><span class="pl-pds">&#39;</span>name<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>supermarket<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>amenity<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>discount_supermarket<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>any<span class="pl-pds">&#39;</span></span>);</td>
      </tr>
      <tr>
        <td id="L354" class="blob-num js-line-number" data-line-number="354"></td>
        <td id="LC354" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> pois_reclassification_array(<span class="pl-s"><span class="pl-pds">&#39;</span>name<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>supermarket<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>amenity<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>hypermarket<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>any<span class="pl-pds">&#39;</span></span>);</td>
      </tr>
      <tr>
        <td id="L355" class="blob-num js-line-number" data-line-number="355"></td>
        <td id="LC355" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> pois_reclassification_array(<span class="pl-s"><span class="pl-pds">&#39;</span>name<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>supermarket<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>amenity<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>no_end_consumer_store<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>any<span class="pl-pds">&#39;</span></span>);</td>
      </tr>
      <tr>
        <td id="L356" class="blob-num js-line-number" data-line-number="356"></td>
        <td id="LC356" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> pois_reclassification_array(<span class="pl-s"><span class="pl-pds">&#39;</span>name<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>supermarket<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>amenity<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>health_food<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>any<span class="pl-pds">&#39;</span></span>);</td>
      </tr>
      <tr>
        <td id="L357" class="blob-num js-line-number" data-line-number="357"></td>
        <td id="LC357" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L358" class="blob-num js-line-number" data-line-number="358"></td>
        <td id="LC358" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span>Refinement Discount Gyms</span></td>
      </tr>
      <tr>
        <td id="L359" class="blob-num js-line-number" data-line-number="359"></td>
        <td id="LC359" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> pois_reclassification_array(<span class="pl-s"><span class="pl-pds">&#39;</span>name<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>gym<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>amenity<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>discount_gym<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>any<span class="pl-pds">&#39;</span></span>);</td>
      </tr>
      <tr>
        <td id="L360" class="blob-num js-line-number" data-line-number="360"></td>
        <td id="LC360" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L361" class="blob-num js-line-number" data-line-number="361"></td>
        <td id="LC361" class="blob-code blob-code-inner js-file-line"><span class="pl-k">UPDATE</span> pois <span class="pl-k">SET</span> amenity <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>organic<span class="pl-pds">&#39;</span></span></td>
      </tr>
      <tr>
        <td id="L362" class="blob-num js-line-number" data-line-number="362"></td>
        <td id="LC362" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> organic <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>only<span class="pl-pds">&#39;</span></span></td>
      </tr>
      <tr>
        <td id="L363" class="blob-num js-line-number" data-line-number="363"></td>
        <td id="LC363" class="blob-code blob-code-inner js-file-line"><span class="pl-k">AND</span> (amenity <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>supermarket<span class="pl-pds">&#39;</span></span> <span class="pl-k">OR</span> amenity <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>convenience<span class="pl-pds">&#39;</span></span>);</td>
      </tr>
      <tr>
        <td id="L364" class="blob-num js-line-number" data-line-number="364"></td>
        <td id="LC364" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L365" class="blob-num js-line-number" data-line-number="365"></td>
        <td id="LC365" class="blob-code blob-code-inner js-file-line"><span class="pl-k">UPDATE</span> pois <span class="pl-k">SET</span> amenity <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>international_supermarket<span class="pl-pds">&#39;</span></span></td>
      </tr>
      <tr>
        <td id="L366" class="blob-num js-line-number" data-line-number="366"></td>
        <td id="LC366" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> origin <span class="pl-k">is not null</span></td>
      </tr>
      <tr>
        <td id="L367" class="blob-num js-line-number" data-line-number="367"></td>
        <td id="LC367" class="blob-code blob-code-inner js-file-line"><span class="pl-k">AND</span> (amenity <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>supermarket<span class="pl-pds">&#39;</span></span> <span class="pl-k">OR</span> amenity <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>convenience<span class="pl-pds">&#39;</span></span>);</td>
      </tr>
      <tr>
        <td id="L368" class="blob-num js-line-number" data-line-number="368"></td>
        <td id="LC368" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L369" class="blob-num js-line-number" data-line-number="369"></td>
        <td id="LC369" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">/*</span>End<span class="pl-c">*/</span></span></td>
      </tr>
      <tr>
        <td id="L370" class="blob-num js-line-number" data-line-number="370"></td>
        <td id="LC370" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L371" class="blob-num js-line-number" data-line-number="371"></td>
        <td id="LC371" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span>Select relevant operators bicycle_rental</span></td>
      </tr>
      <tr>
        <td id="L372" class="blob-num js-line-number" data-line-number="372"></td>
        <td id="LC372" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L373" class="blob-num js-line-number" data-line-number="373"></td>
        <td id="LC373" class="blob-code blob-code-inner js-file-line"><span class="pl-k">DELETE</span> <span class="pl-k">FROM</span> pois </td>
      </tr>
      <tr>
        <td id="L374" class="blob-num js-line-number" data-line-number="374"></td>
        <td id="LC374" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> (NOT <span class="pl-c1">lower</span>(operator) ~~ </td>
      </tr>
      <tr>
        <td id="L375" class="blob-num js-line-number" data-line-number="375"></td>
        <td id="LC375" class="blob-code blob-code-inner js-file-line">ANY</td>
      </tr>
      <tr>
        <td id="L376" class="blob-num js-line-number" data-line-number="376"></td>
        <td id="LC376" class="blob-code blob-code-inner js-file-line">(</td>
      </tr>
      <tr>
        <td id="L377" class="blob-num js-line-number" data-line-number="377"></td>
        <td id="LC377" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">SELECT</span> concat(<span class="pl-s"><span class="pl-pds">&#39;</span>%<span class="pl-pds">&#39;</span></span>,jsonb_object_keys(select_from_variable_container_o(<span class="pl-s"><span class="pl-pds">&#39;</span>pois_search_conditions<span class="pl-pds">&#39;</span></span>)<span class="pl-k">-</span><span class="pl-k">&gt;</span><span class="pl-s"><span class="pl-pds">&#39;</span>operators_bicycle_rental<span class="pl-pds">&#39;</span></span>),<span class="pl-s"><span class="pl-pds">&#39;</span>%<span class="pl-pds">&#39;</span></span>)</td>
      </tr>
      <tr>
        <td id="L378" class="blob-num js-line-number" data-line-number="378"></td>
        <td id="LC378" class="blob-code blob-code-inner js-file-line">)  </td>
      </tr>
      <tr>
        <td id="L379" class="blob-num js-line-number" data-line-number="379"></td>
        <td id="LC379" class="blob-code blob-code-inner js-file-line"><span class="pl-k">OR</span> operator IS <span class="pl-k">NULL</span>) </td>
      </tr>
      <tr>
        <td id="L380" class="blob-num js-line-number" data-line-number="380"></td>
        <td id="LC380" class="blob-code blob-code-inner js-file-line"><span class="pl-k">AND</span> amenity <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>bicycle_rental<span class="pl-pds">&#39;</span></span>;</td>
      </tr>
      <tr>
        <td id="L381" class="blob-num js-line-number" data-line-number="381"></td>
        <td id="LC381" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L382" class="blob-num js-line-number" data-line-number="382"></td>
        <td id="LC382" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L383" class="blob-num js-line-number" data-line-number="383"></td>
        <td id="LC383" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span>INSERT public_transport_stops</span></td>
      </tr>
      <tr>
        <td id="L384" class="blob-num js-line-number" data-line-number="384"></td>
        <td id="LC384" class="blob-code blob-code-inner js-file-line">WITH pt <span class="pl-k">AS</span> (</td>
      </tr>
      <tr>
        <td id="L385" class="blob-num js-line-number" data-line-number="385"></td>
        <td id="LC385" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">SELECT</span> osm_id,<span class="pl-s"><span class="pl-pds">&#39;</span>bus_stop<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> public_transport_stop,name,tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> wheelchair, way <span class="pl-k">as</span> geom <span class="pl-k">FROM</span> planet_osm_point </td>
      </tr>
      <tr>
        <td id="L386" class="blob-num js-line-number" data-line-number="386"></td>
        <td id="LC386" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">WHERE</span> highway <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>bus_stop<span class="pl-pds">&#39;</span></span> <span class="pl-k">AND</span> name <span class="pl-k">IS NOT NULL</span></td>
      </tr>
      <tr>
        <td id="L387" class="blob-num js-line-number" data-line-number="387"></td>
        <td id="LC387" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">UNION ALL</span></td>
      </tr>
      <tr>
        <td id="L388" class="blob-num js-line-number" data-line-number="388"></td>
        <td id="LC388" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">SELECT</span> osm_id,<span class="pl-s"><span class="pl-pds">&#39;</span>bus_stop<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> public_transport_stop,name,tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> wheelchair, way <span class="pl-k">as</span> geom <span class="pl-k">FROM</span> planet_osm_point </td>
      </tr>
      <tr>
        <td id="L389" class="blob-num js-line-number" data-line-number="389"></td>
        <td id="LC389" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">WHERE</span> public_transport <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>platform<span class="pl-pds">&#39;</span></span> <span class="pl-k">AND</span> highway <span class="pl-k">&lt;&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>bus_stop<span class="pl-pds">&#39;</span></span></td>
      </tr>
      <tr>
        <td id="L390" class="blob-num js-line-number" data-line-number="390"></td>
        <td id="LC390" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">AND</span> name <span class="pl-k">IS NOT NULL</span> <span class="pl-k">AND</span> tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>bus<span class="pl-pds">&#39;</span></span><span class="pl-k">=</span><span class="pl-s"><span class="pl-pds">&#39;</span>yes<span class="pl-pds">&#39;</span></span></td>
      </tr>
      <tr>
        <td id="L391" class="blob-num js-line-number" data-line-number="391"></td>
        <td id="LC391" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">UNION ALL</span></td>
      </tr>
      <tr>
        <td id="L392" class="blob-num js-line-number" data-line-number="392"></td>
        <td id="LC392" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">SELECT</span> osm_id,<span class="pl-s"><span class="pl-pds">&#39;</span>tram_stop<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> public_transport_stop,name,tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> wheelchair,way <span class="pl-k">as</span> geom <span class="pl-k">FROM</span> planet_osm_point </td>
      </tr>
      <tr>
        <td id="L393" class="blob-num js-line-number" data-line-number="393"></td>
        <td id="LC393" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">WHERE</span> public_transport <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>stop_position<span class="pl-pds">&#39;</span></span> </td>
      </tr>
      <tr>
        <td id="L394" class="blob-num js-line-number" data-line-number="394"></td>
        <td id="LC394" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">AND</span> tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>tram<span class="pl-pds">&#39;</span></span><span class="pl-k">=</span><span class="pl-s"><span class="pl-pds">&#39;</span>yes<span class="pl-pds">&#39;</span></span></td>
      </tr>
      <tr>
        <td id="L395" class="blob-num js-line-number" data-line-number="395"></td>
        <td id="LC395" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">AND</span> name <span class="pl-k">IS NOT NULL</span></td>
      </tr>
      <tr>
        <td id="L396" class="blob-num js-line-number" data-line-number="396"></td>
        <td id="LC396" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">UNION ALL</span></td>
      </tr>
      <tr>
        <td id="L397" class="blob-num js-line-number" data-line-number="397"></td>
        <td id="LC397" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">SELECT</span> osm_id,<span class="pl-s"><span class="pl-pds">&#39;</span>subway_entrance<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> public_transport,name,tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> wheelchair, way <span class="pl-k">as</span> geom <span class="pl-k">FROM</span> planet_osm_point</td>
      </tr>
      <tr>
        <td id="L398" class="blob-num js-line-number" data-line-number="398"></td>
        <td id="LC398" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">WHERE</span> railway <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>subway_entrance<span class="pl-pds">&#39;</span></span></td>
      </tr>
      <tr>
        <td id="L399" class="blob-num js-line-number" data-line-number="399"></td>
        <td id="LC399" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">UNION ALL</span></td>
      </tr>
      <tr>
        <td id="L400" class="blob-num js-line-number" data-line-number="400"></td>
        <td id="LC400" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">SELECT</span> osm_id,<span class="pl-s"><span class="pl-pds">&#39;</span>rail_station<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> public_transport,name,tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>wheelchair<span class="pl-pds">&#39;</span></span> <span class="pl-k">AS</span> wheelchair,way <span class="pl-k">as</span> geom </td>
      </tr>
      <tr>
        <td id="L401" class="blob-num js-line-number" data-line-number="401"></td>
        <td id="LC401" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">FROM</span> planet_osm_point <span class="pl-k">WHERE</span> railway <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>stop<span class="pl-pds">&#39;</span></span></td>
      </tr>
      <tr>
        <td id="L402" class="blob-num js-line-number" data-line-number="402"></td>
        <td id="LC402" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">AND</span> tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>train<span class="pl-pds">&#39;</span></span> <span class="pl-k">=</span><span class="pl-s"><span class="pl-pds">&#39;</span>yes<span class="pl-pds">&#39;</span></span></td>
      </tr>
      <tr>
        <td id="L403" class="blob-num js-line-number" data-line-number="403"></td>
        <td id="LC403" class="blob-code blob-code-inner js-file-line">)</td>
      </tr>
      <tr>
        <td id="L404" class="blob-num js-line-number" data-line-number="404"></td>
        <td id="LC404" class="blob-code blob-code-inner js-file-line"><span class="pl-k">INSERT INTO</span> pois (osm_id,origin_geometry,amenity,name,wheelchair,geom) </td>
      </tr>
      <tr>
        <td id="L405" class="blob-num js-line-number" data-line-number="405"></td>
        <td id="LC405" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> osm_id,<span class="pl-s"><span class="pl-pds">&#39;</span>point<span class="pl-pds">&#39;</span></span>,public_transport_stop,name,wheelchair,geom </td>
      </tr>
      <tr>
        <td id="L406" class="blob-num js-line-number" data-line-number="406"></td>
        <td id="LC406" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> pt;</td>
      </tr>
      <tr>
        <td id="L407" class="blob-num js-line-number" data-line-number="407"></td>
        <td id="LC407" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L408" class="blob-num js-line-number" data-line-number="408"></td>
        <td id="LC408" class="blob-code blob-code-inner js-file-line">DO $$                  </td>
      </tr>
      <tr>
        <td id="L409" class="blob-num js-line-number" data-line-number="409"></td>
        <td id="LC409" class="blob-code blob-code-inner js-file-line">    <span class="pl-k">BEGIN</span> </td>
      </tr>
      <tr>
        <td id="L410" class="blob-num js-line-number" data-line-number="410"></td>
        <td id="LC410" class="blob-code blob-code-inner js-file-line">        IF EXISTS</td>
      </tr>
      <tr>
        <td id="L411" class="blob-num js-line-number" data-line-number="411"></td>
        <td id="LC411" class="blob-code blob-code-inner js-file-line">            ( <span class="pl-k">SELECT</span> <span class="pl-c1">1</span></td>
      </tr>
      <tr>
        <td id="L412" class="blob-num js-line-number" data-line-number="412"></td>
        <td id="LC412" class="blob-code blob-code-inner js-file-line">              <span class="pl-k">FROM</span>   <span class="pl-c1">information_schema</span>.<span class="pl-c1">tables</span> </td>
      </tr>
      <tr>
        <td id="L413" class="blob-num js-line-number" data-line-number="413"></td>
        <td id="LC413" class="blob-code blob-code-inner js-file-line">              <span class="pl-k">WHERE</span>  table_schema <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>public<span class="pl-pds">&#39;</span></span></td>
      </tr>
      <tr>
        <td id="L414" class="blob-num js-line-number" data-line-number="414"></td>
        <td id="LC414" class="blob-code blob-code-inner js-file-line">              <span class="pl-k">AND</span>    table_name <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>pois_insert_no_fusion<span class="pl-pds">&#39;</span></span></td>
      </tr>
      <tr>
        <td id="L415" class="blob-num js-line-number" data-line-number="415"></td>
        <td id="LC415" class="blob-code blob-code-inner js-file-line">            )</td>
      </tr>
      <tr>
        <td id="L416" class="blob-num js-line-number" data-line-number="416"></td>
        <td id="LC416" class="blob-code blob-code-inner js-file-line">        THEN</td>
      </tr>
      <tr>
        <td id="L417" class="blob-num js-line-number" data-line-number="417"></td>
        <td id="LC417" class="blob-code blob-code-inner js-file-line">			<span class="pl-k">INSERT INTO</span> pois (origin_geometry,amenity,name,geom)</td>
      </tr>
      <tr>
        <td id="L418" class="blob-num js-line-number" data-line-number="418"></td>
        <td id="LC418" class="blob-code blob-code-inner js-file-line">			<span class="pl-k">SELECT</span> <span class="pl-s"><span class="pl-pds">&#39;</span>point<span class="pl-pds">&#39;</span></span>, amenity, name, geom </td>
      </tr>
      <tr>
        <td id="L419" class="blob-num js-line-number" data-line-number="419"></td>
        <td id="LC419" class="blob-code blob-code-inner js-file-line">			<span class="pl-k">FROM</span> pois_insert_no_fusion;</td>
      </tr>
      <tr>
        <td id="L420" class="blob-num js-line-number" data-line-number="420"></td>
        <td id="LC420" class="blob-code blob-code-inner js-file-line">		END IF;</td>
      </tr>
      <tr>
        <td id="L421" class="blob-num js-line-number" data-line-number="421"></td>
        <td id="LC421" class="blob-code blob-code-inner js-file-line">    END</td>
      </tr>
      <tr>
        <td id="L422" class="blob-num js-line-number" data-line-number="422"></td>
        <td id="LC422" class="blob-code blob-code-inner js-file-line">$$ ;</td>
      </tr>
      <tr>
        <td id="L423" class="blob-num js-line-number" data-line-number="423"></td>
        <td id="LC423" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L424" class="blob-num js-line-number" data-line-number="424"></td>
        <td id="LC424" class="blob-code blob-code-inner js-file-line">WITH x <span class="pl-k">AS</span> (</td>
      </tr>
      <tr>
        <td id="L425" class="blob-num js-line-number" data-line-number="425"></td>
        <td id="LC425" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">SELECT</span> <span class="pl-s"><span class="pl-pds">&#39;</span>subway<span class="pl-pds">&#39;</span></span> <span class="pl-k">as</span> public_transport,name,way <span class="pl-k">as</span> geom  <span class="pl-k">FROM</span> planet_osm_point </td>
      </tr>
      <tr>
        <td id="L426" class="blob-num js-line-number" data-line-number="426"></td>
        <td id="LC426" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">WHERE</span> public_transport <span class="pl-k">=</span><span class="pl-s"><span class="pl-pds">&#39;</span>station<span class="pl-pds">&#39;</span></span> </td>
      </tr>
      <tr>
        <td id="L427" class="blob-num js-line-number" data-line-number="427"></td>
        <td id="LC427" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">AND</span> tags <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>subway<span class="pl-pds">&#39;</span></span> <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>yes<span class="pl-pds">&#39;</span></span> <span class="pl-k">AND</span> railway <span class="pl-k">&lt;&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>proposed<span class="pl-pds">&#39;</span></span></td>
      </tr>
      <tr>
        <td id="L428" class="blob-num js-line-number" data-line-number="428"></td>
        <td id="LC428" class="blob-code blob-code-inner js-file-line">),</td>
      </tr>
      <tr>
        <td id="L429" class="blob-num js-line-number" data-line-number="429"></td>
        <td id="LC429" class="blob-code blob-code-inner js-file-line">close_entrances <span class="pl-k">AS</span> (</td>
      </tr>
      <tr>
        <td id="L430" class="blob-num js-line-number" data-line-number="430"></td>
        <td id="LC430" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">SELECT</span> <span class="pl-c1">p</span>.<span class="pl-c1">geom</span>,<span class="pl-c1">x</span>.<span class="pl-c1">name</span>,<span class="pl-c1">min</span>(st_distance(<span class="pl-c1">p</span>.<span class="pl-c1">geom</span>::geography,<span class="pl-c1">x</span>.<span class="pl-c1">geom</span>::geography))</td>
      </tr>
      <tr>
        <td id="L431" class="blob-num js-line-number" data-line-number="431"></td>
        <td id="LC431" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">FROM</span> pois p, x</td>
      </tr>
      <tr>
        <td id="L432" class="blob-num js-line-number" data-line-number="432"></td>
        <td id="LC432" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">WHERE</span> <span class="pl-c1">p</span>.<span class="pl-c1">geom</span> &amp;&amp; ST_Buffer(<span class="pl-c1">x</span>.<span class="pl-c1">geom</span>::geography,<span class="pl-c1">500</span>)::geometry</td>
      </tr>
      <tr>
        <td id="L433" class="blob-num js-line-number" data-line-number="433"></td>
        <td id="LC433" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">GROUP BY</span> <span class="pl-c1">p</span>.<span class="pl-c1">geom</span>,<span class="pl-c1">x</span>.<span class="pl-c1">name</span></td>
      </tr>
      <tr>
        <td id="L434" class="blob-num js-line-number" data-line-number="434"></td>
        <td id="LC434" class="blob-code blob-code-inner js-file-line">)</td>
      </tr>
      <tr>
        <td id="L435" class="blob-num js-line-number" data-line-number="435"></td>
        <td id="LC435" class="blob-code blob-code-inner js-file-line"><span class="pl-k">UPDATE</span> pois p <span class="pl-k">set</span> name <span class="pl-k">=</span> <span class="pl-c1">c</span>.<span class="pl-c1">name</span> </td>
      </tr>
      <tr>
        <td id="L436" class="blob-num js-line-number" data-line-number="436"></td>
        <td id="LC436" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> close_entrances c</td>
      </tr>
      <tr>
        <td id="L437" class="blob-num js-line-number" data-line-number="437"></td>
        <td id="LC437" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> <span class="pl-c1">p</span>.<span class="pl-c1">geom</span> <span class="pl-k">=</span> <span class="pl-c1">c</span>.<span class="pl-c1">geom</span></td>
      </tr>
      <tr>
        <td id="L438" class="blob-num js-line-number" data-line-number="438"></td>
        <td id="LC438" class="blob-code blob-code-inner js-file-line"><span class="pl-k">AND</span> amenity <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>subway_entrance<span class="pl-pds">&#39;</span></span>;</td>
      </tr>
      <tr>
        <td id="L439" class="blob-num js-line-number" data-line-number="439"></td>
        <td id="LC439" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L440" class="blob-num js-line-number" data-line-number="440"></td>
        <td id="LC440" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span> Multipoint for Sports center and waterparks</span></td>
      </tr>
      <tr>
        <td id="L441" class="blob-num js-line-number" data-line-number="441"></td>
        <td id="LC441" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L442" class="blob-num js-line-number" data-line-number="442"></td>
        <td id="LC442" class="blob-code blob-code-inner js-file-line"><span class="pl-k">DROP</span> <span class="pl-k">TABLE</span> IF EXISTS community_sports_center;</td>
      </tr>
      <tr>
        <td id="L443" class="blob-num js-line-number" data-line-number="443"></td>
        <td id="LC443" class="blob-code blob-code-inner js-file-line"><span class="pl-k">DROP</span> <span class="pl-k">TABLE</span> IF EXISTS waterpark;</td>
      </tr>
      <tr>
        <td id="L444" class="blob-num js-line-number" data-line-number="444"></td>
        <td id="LC444" class="blob-code blob-code-inner js-file-line"><span class="pl-k">CREATE</span> <span class="pl-k">TABLE</span> <span class="pl-en">community_sports_center</span> (<span class="pl-k">LIKE</span> planet_osm_polygon INCLUDING INDEXES);</td>
      </tr>
      <tr>
        <td id="L445" class="blob-num js-line-number" data-line-number="445"></td>
        <td id="LC445" class="blob-code blob-code-inner js-file-line"><span class="pl-k">INSERT INTO</span> community_sports_center</td>
      </tr>
      <tr>
        <td id="L446" class="blob-num js-line-number" data-line-number="446"></td>
        <td id="LC446" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> <span class="pl-k">*</span> </td>
      </tr>
      <tr>
        <td id="L447" class="blob-num js-line-number" data-line-number="447"></td>
        <td id="LC447" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> planet_osm_polygon </td>
      </tr>
      <tr>
        <td id="L448" class="blob-num js-line-number" data-line-number="448"></td>
        <td id="LC448" class="blob-code blob-code-inner js-file-line"><span class="pl-k">WHERE</span> </td>
      </tr>
      <tr>
        <td id="L449" class="blob-num js-line-number" data-line-number="449"></td>
        <td id="LC449" class="blob-code blob-code-inner js-file-line">(</td>
      </tr>
      <tr>
        <td id="L450" class="blob-num js-line-number" data-line-number="450"></td>
        <td id="LC450" class="blob-code blob-code-inner js-file-line">	(leisure <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>sports_centre<span class="pl-pds">&#39;</span></span> <span class="pl-k">AND</span> </td>
      </tr>
      <tr>
        <td id="L451" class="blob-num js-line-number" data-line-number="451"></td>
        <td id="LC451" class="blob-code blob-code-inner js-file-line">	<span class="pl-c1">lower</span>(name) ~~ ANY (ARRAY(<span class="pl-k">SELECT</span> <span class="pl-s"><span class="pl-pds">&#39;</span>%<span class="pl-pds">&#39;</span></span><span class="pl-k">||</span>jsonb_array_elements_text(select_from_variable_container_o(<span class="pl-s"><span class="pl-pds">&#39;</span>pois_search_conditions<span class="pl-pds">&#39;</span></span>) <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>community_sport_centre<span class="pl-pds">&#39;</span></span>) <span class="pl-k">||</span> <span class="pl-s"><span class="pl-pds">&#39;</span>%<span class="pl-pds">&#39;</span></span>)))</td>
      </tr>
      <tr>
        <td id="L452" class="blob-num js-line-number" data-line-number="452"></td>
        <td id="LC452" class="blob-code blob-code-inner js-file-line">	<span class="pl-k">OR</span> </td>
      </tr>
      <tr>
        <td id="L453" class="blob-num js-line-number" data-line-number="453"></td>
        <td id="LC453" class="blob-code blob-code-inner js-file-line">	(landuse <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>recreation_ground<span class="pl-pds">&#39;</span></span> <span class="pl-k">AND</span> <span class="pl-c1">lower</span>(name) ~~ ANY (ARRAY(<span class="pl-k">SELECT</span> <span class="pl-s"><span class="pl-pds">&#39;</span>%<span class="pl-pds">&#39;</span></span><span class="pl-k">||</span>jsonb_array_elements_text(select_from_variable_container_o(<span class="pl-s"><span class="pl-pds">&#39;</span>pois_search_conditions<span class="pl-pds">&#39;</span></span>) <span class="pl-k">-</span><span class="pl-k">&gt;</span> <span class="pl-s"><span class="pl-pds">&#39;</span>community_sport_centre<span class="pl-pds">&#39;</span></span>) <span class="pl-k">||</span> <span class="pl-s"><span class="pl-pds">&#39;</span>%<span class="pl-pds">&#39;</span></span>)</td>
      </tr>
      <tr>
        <td id="L454" class="blob-num js-line-number" data-line-number="454"></td>
        <td id="LC454" class="blob-code blob-code-inner js-file-line">))</td>
      </tr>
      <tr>
        <td id="L455" class="blob-num js-line-number" data-line-number="455"></td>
        <td id="LC455" class="blob-code blob-code-inner js-file-line">)</td>
      </tr>
      <tr>
        <td id="L456" class="blob-num js-line-number" data-line-number="456"></td>
        <td id="LC456" class="blob-code blob-code-inner js-file-line"><span class="pl-k">AND</span> amenity IS <span class="pl-k">NULL</span> </td>
      </tr>
      <tr>
        <td id="L457" class="blob-num js-line-number" data-line-number="457"></td>
        <td id="LC457" class="blob-code blob-code-inner js-file-line"><span class="pl-k">AND</span> NOT (building <span class="pl-k">IS NOT NULL</span> <span class="pl-k">AND</span> sport IS <span class="pl-k">null</span>);</td>
      </tr>
      <tr>
        <td id="L458" class="blob-num js-line-number" data-line-number="458"></td>
        <td id="LC458" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L459" class="blob-num js-line-number" data-line-number="459"></td>
        <td id="LC459" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> derive_access_from_polygons(<span class="pl-s"><span class="pl-pds">&#39;</span>community_sports_center<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>community_sports_center<span class="pl-pds">&#39;</span></span>);</td>
      </tr>
      <tr>
        <td id="L460" class="blob-num js-line-number" data-line-number="460"></td>
        <td id="LC460" class="blob-code blob-code-inner js-file-line"><span class="pl-k">DROP</span> <span class="pl-k">TABLE</span> IF EXISTS community_sports_center;</td>
      </tr>
      <tr>
        <td id="L461" class="blob-num js-line-number" data-line-number="461"></td>
        <td id="LC461" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L462" class="blob-num js-line-number" data-line-number="462"></td>
        <td id="LC462" class="blob-code blob-code-inner js-file-line"><span class="pl-k">CREATE</span> <span class="pl-k">TABLE</span> <span class="pl-en">waterpark</span> (<span class="pl-k">LIKE</span> planet_osm_polygon INCLUDING INDEXES);</td>
      </tr>
      <tr>
        <td id="L463" class="blob-num js-line-number" data-line-number="463"></td>
        <td id="LC463" class="blob-code blob-code-inner js-file-line"><span class="pl-k">INSERT INTO</span> waterpark</td>
      </tr>
      <tr>
        <td id="L464" class="blob-num js-line-number" data-line-number="464"></td>
        <td id="LC464" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> <span class="pl-k">*</span> </td>
      </tr>
      <tr>
        <td id="L465" class="blob-num js-line-number" data-line-number="465"></td>
        <td id="LC465" class="blob-code blob-code-inner js-file-line"><span class="pl-k">FROM</span> planet_osm_polygon <span class="pl-k">WHERE</span> leisure <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>water_park<span class="pl-pds">&#39;</span></span> <span class="pl-k">AND</span> amenity IS <span class="pl-k">NULL</span>;</td>
      </tr>
      <tr>
        <td id="L466" class="blob-num js-line-number" data-line-number="466"></td>
        <td id="LC466" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> derive_access_from_polygons(<span class="pl-s"><span class="pl-pds">&#39;</span>waterpark<span class="pl-pds">&#39;</span></span>,<span class="pl-s"><span class="pl-pds">&#39;</span>waterpark<span class="pl-pds">&#39;</span></span>);</td>
      </tr>
      <tr>
        <td id="L467" class="blob-num js-line-number" data-line-number="467"></td>
        <td id="LC467" class="blob-code blob-code-inner js-file-line"><span class="pl-k">DROP</span> <span class="pl-k">TABLE</span> IF EXISTS waterpark;</td>
      </tr>
      <tr>
        <td id="L468" class="blob-num js-line-number" data-line-number="468"></td>
        <td id="LC468" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L469" class="blob-num js-line-number" data-line-number="469"></td>
        <td id="LC469" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span> If custom_pois exists, run pois fusion </span></td>
      </tr>
      <tr>
        <td id="L470" class="blob-num js-line-number" data-line-number="470"></td>
        <td id="LC470" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L471" class="blob-num js-line-number" data-line-number="471"></td>
        <td id="LC471" class="blob-code blob-code-inner js-file-line">DO $$                  </td>
      </tr>
      <tr>
        <td id="L472" class="blob-num js-line-number" data-line-number="472"></td>
        <td id="LC472" class="blob-code blob-code-inner js-file-line">    <span class="pl-k">BEGIN</span> </td>
      </tr>
      <tr>
        <td id="L473" class="blob-num js-line-number" data-line-number="473"></td>
        <td id="LC473" class="blob-code blob-code-inner js-file-line">        IF EXISTS</td>
      </tr>
      <tr>
        <td id="L474" class="blob-num js-line-number" data-line-number="474"></td>
        <td id="LC474" class="blob-code blob-code-inner js-file-line">            ( <span class="pl-k">SELECT</span> <span class="pl-c1">1</span></td>
      </tr>
      <tr>
        <td id="L475" class="blob-num js-line-number" data-line-number="475"></td>
        <td id="LC475" class="blob-code blob-code-inner js-file-line">              <span class="pl-k">FROM</span>   <span class="pl-c1">information_schema</span>.<span class="pl-c1">tables</span> </td>
      </tr>
      <tr>
        <td id="L476" class="blob-num js-line-number" data-line-number="476"></td>
        <td id="LC476" class="blob-code blob-code-inner js-file-line">              <span class="pl-k">WHERE</span>  table_schema <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>public<span class="pl-pds">&#39;</span></span></td>
      </tr>
      <tr>
        <td id="L477" class="blob-num js-line-number" data-line-number="477"></td>
        <td id="LC477" class="blob-code blob-code-inner js-file-line">              <span class="pl-k">AND</span>    table_name <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>custom_pois<span class="pl-pds">&#39;</span></span></td>
      </tr>
      <tr>
        <td id="L478" class="blob-num js-line-number" data-line-number="478"></td>
        <td id="LC478" class="blob-code blob-code-inner js-file-line">            )</td>
      </tr>
      <tr>
        <td id="L479" class="blob-num js-line-number" data-line-number="479"></td>
        <td id="LC479" class="blob-code blob-code-inner js-file-line">        THEN</td>
      </tr>
      <tr>
        <td id="L480" class="blob-num js-line-number" data-line-number="480"></td>
        <td id="LC480" class="blob-code blob-code-inner js-file-line">			<span class="pl-c"><span class="pl-c">--</span>Run pois_fusion</span></td>
      </tr>
      <tr>
        <td id="L481" class="blob-num js-line-number" data-line-number="481"></td>
        <td id="LC481" class="blob-code blob-code-inner js-file-line">			PERFORM pois_fusion();</td>
      </tr>
      <tr>
        <td id="L482" class="blob-num js-line-number" data-line-number="482"></td>
        <td id="LC482" class="blob-code blob-code-inner js-file-line">        END IF ;</td>
      </tr>
      <tr>
        <td id="L483" class="blob-num js-line-number" data-line-number="483"></td>
        <td id="LC483" class="blob-code blob-code-inner js-file-line">    END</td>
      </tr>
      <tr>
        <td id="L484" class="blob-num js-line-number" data-line-number="484"></td>
        <td id="LC484" class="blob-code blob-code-inner js-file-line">$$ ;</td>
      </tr>
      <tr>
        <td id="L485" class="blob-num js-line-number" data-line-number="485"></td>
        <td id="LC485" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L486" class="blob-num js-line-number" data-line-number="486"></td>
        <td id="LC486" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L487" class="blob-num js-line-number" data-line-number="487"></td>
        <td id="LC487" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span>CREATE copy of pois for scenarios</span></td>
      </tr>
      <tr>
        <td id="L488" class="blob-num js-line-number" data-line-number="488"></td>
        <td id="LC488" class="blob-code blob-code-inner js-file-line"><span class="pl-k">DROP</span> <span class="pl-k">TABLE</span> IF EXISTS pois_userinput;</td>
      </tr>
      <tr>
        <td id="L489" class="blob-num js-line-number" data-line-number="489"></td>
        <td id="LC489" class="blob-code blob-code-inner js-file-line"><span class="pl-k">CREATE</span> <span class="pl-k">TABLE</span> <span class="pl-en">pois_userinput</span> (<span class="pl-k">like</span> pois INCLUDING ALL);</td>
      </tr>
      <tr>
        <td id="L490" class="blob-num js-line-number" data-line-number="490"></td>
        <td id="LC490" class="blob-code blob-code-inner js-file-line"><span class="pl-k">INSERT INTO</span> pois_userinput</td>
      </tr>
      <tr>
        <td id="L491" class="blob-num js-line-number" data-line-number="491"></td>
        <td id="LC491" class="blob-code blob-code-inner js-file-line"><span class="pl-k">SELECT</span> <span class="pl-k">*</span> <span class="pl-k">FROM</span> pois;</td>
      </tr>
      <tr>
        <td id="L492" class="blob-num js-line-number" data-line-number="492"></td>
        <td id="LC492" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L493" class="blob-num js-line-number" data-line-number="493"></td>
        <td id="LC493" class="blob-code blob-code-inner js-file-line"><span class="pl-k">ALTER</span> <span class="pl-k">TABLE</span> pois_userinput ADD COLUMN userid <span class="pl-k">integer</span>;</td>
      </tr>
      <tr>
        <td id="L494" class="blob-num js-line-number" data-line-number="494"></td>
        <td id="LC494" class="blob-code blob-code-inner js-file-line"><span class="pl-k">CREATE</span> <span class="pl-k">INDEX</span> <span class="pl-en">ON</span> pois_userinput(userid);</td>
      </tr>
      <tr>
        <td id="L495" class="blob-num js-line-number" data-line-number="495"></td>
        <td id="LC495" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L496" class="blob-num js-line-number" data-line-number="496"></td>
        <td id="LC496" class="blob-code blob-code-inner js-file-line"><span class="pl-c"><span class="pl-c">--</span>Add Foreign Key to pois_userinput </span></td>
      </tr>
      <tr>
        <td id="L497" class="blob-num js-line-number" data-line-number="497"></td>
        <td id="LC497" class="blob-code blob-code-inner js-file-line"><span class="pl-k">ALTER</span> <span class="pl-k">TABLE</span> pois_userinput ADD COLUMN pois_modified_id <span class="pl-k">integer</span>; </td>
      </tr>
      <tr>
        <td id="L498" class="blob-num js-line-number" data-line-number="498"></td>
        <td id="LC498" class="blob-code blob-code-inner js-file-line"><span class="pl-k">ALTER</span> <span class="pl-k">TABLE</span> pois_userinput</td>
      </tr>
      <tr>
        <td id="L499" class="blob-num js-line-number" data-line-number="499"></td>
        <td id="LC499" class="blob-code blob-code-inner js-file-line">ADD <span class="pl-k">CONSTRAINT</span> pois_userinput_id_fkey <span class="pl-k">FOREIGN KEY</span> (pois_modified_id) </td>
      </tr>
      <tr>
        <td id="L500" class="blob-num js-line-number" data-line-number="500"></td>
        <td id="LC500" class="blob-code blob-code-inner js-file-line"><span class="pl-k">REFERENCES</span> pois_modified(id) <span class="pl-k">ON DELETE CASCADE</span>;</td>
      </tr>
</table>

  <details class="details-reset details-overlay BlobToolbar position-absolute js-file-line-actions dropdown d-none" aria-hidden="true">
    <summary class="btn-octicon ml-0 px-2 p-0 bg-white border border-gray-dark rounded-1" aria-label="Inline file action toolbar">
      <svg class="octicon octicon-kebab-horizontal" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path d="M8 9a1.5 1.5 0 100-3 1.5 1.5 0 000 3zM1.5 9a1.5 1.5 0 100-3 1.5 1.5 0 000 3zm13 0a1.5 1.5 0 100-3 1.5 1.5 0 000 3z"></path></svg>
    </summary>
    <details-menu>
      <ul class="BlobToolbar-dropdown dropdown-menu dropdown-menu-se mt-2" style="width:185px">
        <li>
          <clipboard-copy role="menuitem" class="dropdown-item" id="js-copy-lines" style="cursor:pointer;">
            Copy lines
          </clipboard-copy>
        </li>
        <li>
          <clipboard-copy role="menuitem" class="dropdown-item" id="js-copy-permalink" style="cursor:pointer;">
            Copy permalink
          </clipboard-copy>
        </li>
        <li><a class="dropdown-item js-update-url-with-hash" id="js-view-git-blame" role="menuitem" href="/goat-community/goat/blame/d429666efd81bc4dfd8a1f8425f51bdf7eafcd2c/app/database/data_preparation/SQL/pois.sql">View git blame</a></li>
          <li><a class="dropdown-item" id="js-new-issue" role="menuitem" href="/goat-community/goat/issues/new">Reference in new issue</a></li>
      </ul>
    </details-menu>
  </details>

  </div>

    </div>

  


  <details class="details-reset details-overlay details-overlay-dark" id="jumpto-line-details-dialog">
    <summary data-hotkey="l" aria-label="Jump to line"></summary>
    <details-dialog class="Box Box--overlay d-flex flex-column anim-fade-in fast linejump" aria-label="Jump to line">
      <!-- '"` --><!-- </textarea></xmp> --></option></form><form class="js-jump-to-line-form Box-body d-flex" action="" accept-charset="UTF-8" method="get">
        <input class="form-control flex-auto mr-3 linejump-input js-jump-to-line-field" type="text" placeholder="Jump to line&hellip;" aria-label="Jump to line" autofocus>
        <button type="submit" class="btn" data-close-dialog>Go</button>
</form>    </details-dialog>
  </details>




  </div>
</div>

    </main>
  </div>
  

  </div>

        
<div class="footer container-xl width-full p-responsive" role="contentinfo">
  <div class="position-relative d-flex flex-row-reverse flex-lg-row flex-wrap flex-lg-nowrap flex-justify-center flex-lg-justify-between pt-6 pb-2 mt-6 f6 text-gray border-top border-gray-light ">
    <ul class="list-style-none d-flex flex-wrap col-12 col-lg-5 flex-justify-center flex-lg-justify-between mb-2 mb-lg-0">
      <li class="mr-3 mr-lg-0">&copy; 2020 GitHub, Inc.</li>
        <li class="mr-3 mr-lg-0"><a data-ga-click="Footer, go to terms, text:terms" href="https://github.com/site/terms">Terms</a></li>
        <li class="mr-3 mr-lg-0"><a data-ga-click="Footer, go to privacy, text:privacy" href="https://github.com/site/privacy">Privacy</a></li>
        <li class="mr-3 mr-lg-0"><a data-ga-click="Footer, go to security, text:security" href="https://github.com/security">Security</a></li>
        <li class="mr-3 mr-lg-0"><a href="https://githubstatus.com/" data-ga-click="Footer, go to status, text:status">Status</a></li>
        <li><a data-ga-click="Footer, go to help, text:help" href="https://docs.github.com">Help</a></li>

    </ul>

    <a aria-label="Homepage" title="GitHub" class="footer-octicon d-none d-lg-block mx-lg-4" href="https://github.com">
      <svg height="24" class="octicon octicon-mark-github" viewBox="0 0 16 16" version="1.1" width="24" aria-hidden="true"><path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path></svg>
</a>
   <ul class="list-style-none d-flex flex-wrap col-12 col-lg-5 flex-justify-center flex-lg-justify-between mb-2 mb-lg-0">
        <li class="mr-3 mr-lg-0"><a data-ga-click="Footer, go to contact, text:contact" href="https://github.com/contact">Contact GitHub</a></li>
        <li class="mr-3 mr-lg-0"><a href="https://github.com/pricing" data-ga-click="Footer, go to Pricing, text:Pricing">Pricing</a></li>
      <li class="mr-3 mr-lg-0"><a href="https://docs.github.com" data-ga-click="Footer, go to api, text:api">API</a></li>
      <li class="mr-3 mr-lg-0"><a href="https://services.github.com" data-ga-click="Footer, go to training, text:training">Training</a></li>
        <li class="mr-3 mr-lg-0"><a href="https://github.blog" data-ga-click="Footer, go to blog, text:blog">Blog</a></li>
        <li><a data-ga-click="Footer, go to about, text:about" href="https://github.com/about">About</a></li>
    </ul>
  </div>
  <div class="d-flex flex-justify-center pb-6">
    <span class="f6 text-gray-light"></span>
  </div>
</div>



  <div id="ajax-error-message" class="ajax-error-message flash flash-error">
    <svg class="octicon octicon-alert" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M8.22 1.754a.25.25 0 00-.44 0L1.698 13.132a.25.25 0 00.22.368h12.164a.25.25 0 00.22-.368L8.22 1.754zm-1.763-.707c.659-1.234 2.427-1.234 3.086 0l6.082 11.378A1.75 1.75 0 0114.082 15H1.918a1.75 1.75 0 01-1.543-2.575L6.457 1.047zM9 11a1 1 0 11-2 0 1 1 0 012 0zm-.25-5.25a.75.75 0 00-1.5 0v2.5a.75.75 0 001.5 0v-2.5z"></path></svg>
    <button type="button" class="flash-close js-ajax-error-dismiss" aria-label="Dismiss error">
      <svg class="octicon octicon-x" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M3.72 3.72a.75.75 0 011.06 0L8 6.94l3.22-3.22a.75.75 0 111.06 1.06L9.06 8l3.22 3.22a.75.75 0 11-1.06 1.06L8 9.06l-3.22 3.22a.75.75 0 01-1.06-1.06L6.94 8 3.72 4.78a.75.75 0 010-1.06z"></path></svg>
    </button>
    You can’t perform that action at this time.
  </div>


    <script crossorigin="anonymous" async="async" integrity="sha512-bn/3rKJzBl2H64K38R8KaVcT26vKK7BJQC59lwYc+9fjlHzmy0fwh+hzBtsgTdhIi13dxjzNKWhdSN8WTM9qUw==" type="application/javascript" id="js-conditional-compat" data-src="https://github.githubassets.com/assets/compat-bootstrap-6e7ff7ac.js"></script>
    <script crossorigin="anonymous" integrity="sha512-CxjaMepCmi+z0LTeztU2S8qGD25LyHD6j9t0RSPevy63trFWJVwUM6ipAVLgtpMBBgZ53wq8JPkSeQ6ruaZL2w==" type="application/javascript" src="https://github.githubassets.com/assets/environment-bootstrap-0b18da31.js"></script>
    <script crossorigin="anonymous" async="async" integrity="sha512-ZpT71hbwZH9CGy7BM/GLovEPgyslK7oJpsKzHFJv5wMAhVrxsGpXYoF7aMHGrOu3SQZd9cv/HN+2dn2d/FNx/A==" type="application/javascript" src="https://github.githubassets.com/assets/vendor-6694fbd6.js"></script>
    <script crossorigin="anonymous" async="async" integrity="sha512-cvRQ/2/cKbueC6DEML4Z6tgaTYWc2rbEwXFTUvqZls7IizI5TuSOBhua5UgHHOSvEt2mm3KpB6FxuAOEtz+mTg==" type="application/javascript" src="https://github.githubassets.com/assets/frameworks-72f450ff.js"></script>
    
    <script crossorigin="anonymous" async="async" integrity="sha512-asendBl8xOaEqbbOmG2teQ8I2X/O7pS3103VUc5Kv4G+RvxIv/TlUWL8VhxCEXz4g5HSDMRj4T8uCRmbyvb0Og==" type="application/javascript" src="https://github.githubassets.com/assets/behaviors-bootstrap-6ac7a774.js"></script>
    
      <script crossorigin="anonymous" async="async" integrity="sha512-TjmDUfspgN28WRWfc01tOL0BFS8pI/TAi8TQ665TcA3jG1C3QgfFu0YKa32Z03rlEL8dukbsy+amwBzgGyjESQ==" type="application/javascript" data-module-id="./Sortable.js" data-src="https://github.githubassets.com/assets/Sortable-4e398351.js"></script>
      <script crossorigin="anonymous" async="async" integrity="sha512-8hScl0DkWwAjCqAQA50kQOn2QTYfPcKEyJjkKYtjGB88r9GB/6kmBBsneJPgwhW3yewwt64ABgsQGpQSLX8zpg==" type="application/javascript" data-module-id="./contributions-spider-graph.js" data-src="https://github.githubassets.com/assets/contributions-spider-graph-f2149c97.js"></script>
      <script crossorigin="anonymous" async="async" integrity="sha512-QOViDUFlNJwNDkBXlntZ4AUm/OFx3TuM7jg4Z1tb3E7dnf3V5p3Oh3E8cwRdjDMDBp4LyOdoBFIhur0biAIdlw==" type="application/javascript" data-module-id="./drag-drop.js" data-src="https://github.githubassets.com/assets/drag-drop-40e5620d.js"></script>
      <script crossorigin="anonymous" async="async" integrity="sha512-iLuC2weaJqL9mYAud2WDWjhd8cJe8dXVxw2KhCH2Rnj6WJvTzlZRmvTtL09wNWX6nRze/TDaQ7gq7BFLchaDYg==" type="application/javascript" data-module-id="./image-crop-element-loader.js" data-src="https://github.githubassets.com/assets/image-crop-element-loader-88bb82db.js"></script>
      <script crossorigin="anonymous" async="async" integrity="sha512-h6a6OmeoK5aqV+JBs2RH8D1xQ1IS4k67sOi5DUmHMV6dv5xVP4Wj37fKucTbjnvuT1IIO4bC/qfRl+BrCMigjg==" type="application/javascript" data-module-id="./jump-to.js" data-src="https://github.githubassets.com/assets/jump-to-87a6ba3a.js"></script>
      <script crossorigin="anonymous" async="async" integrity="sha512-HzWUeLy0p20M4Lc3+EerTwy/VaH3vMuKLvhFJr0PsJfKXnsD9oy5SfashhxStUirglhYZUB4fLYQRM1uzrFyNg==" type="application/javascript" data-module-id="./profile-pins-element.js" data-src="https://github.githubassets.com/assets/profile-pins-element-1f359478.js"></script>
      <script crossorigin="anonymous" async="async" integrity="sha512-qECv/jhsvLFN77eGNu0cjMR2+zvAlLyhQVTnmayJc5OLZoxMLjQZxZW1hK/dhcYro6Wec/aiF21HYf2N5OilYQ==" type="application/javascript" data-module-id="./randomColor.js" data-src="https://github.githubassets.com/assets/randomColor-a840affe.js"></script>
      <script crossorigin="anonymous" async="async" integrity="sha512-mHqsE5aQq7fAmmLd0epHBJK8rn8DOVnjW2YQOT8wvsN1oLrypw0cDFmwXPDwbMghHyo4kKiOtVJ/kEsEzwwibw==" type="application/javascript" data-module-id="./tweetsodium.js" data-src="https://github.githubassets.com/assets/tweetsodium-987aac13.js"></script>
      <script crossorigin="anonymous" async="async" integrity="sha512-WIOX7irV0ZR7jHpy3hhnUvbOMV6Zfu71QFQaANL5zG1k648Mv703s+V2ohGSEhdwf1VC+Bw/NdgyWIQBt+YJLA==" type="application/javascript" data-module-id="./user-status-submit.js" data-src="https://github.githubassets.com/assets/user-status-submit-588397ee.js"></script>
    
    <script crossorigin="anonymous" async="async" integrity="sha512-Iklsy9YupvgRWe3v9SejEpXhpW3E8+fbRMj46o4nSgLQOmuJbNrYSXBdP08V2fZjf9NGh6ME+7XapmN9UNLcmw==" type="application/javascript" src="https://github.githubassets.com/assets/github-bootstrap-22496ccb.js"></script>
  <div class="js-stale-session-flash flash flash-warn flash-banner" hidden
    >
    <svg class="octicon octicon-alert" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M8.22 1.754a.25.25 0 00-.44 0L1.698 13.132a.25.25 0 00.22.368h12.164a.25.25 0 00.22-.368L8.22 1.754zm-1.763-.707c.659-1.234 2.427-1.234 3.086 0l6.082 11.378A1.75 1.75 0 0114.082 15H1.918a1.75 1.75 0 01-1.543-2.575L6.457 1.047zM9 11a1 1 0 11-2 0 1 1 0 012 0zm-.25-5.25a.75.75 0 00-1.5 0v2.5a.75.75 0 001.5 0v-2.5z"></path></svg>
    <span class="js-stale-session-flash-signed-in" hidden>You signed in with another tab or window. <a href="">Reload</a> to refresh your session.</span>
    <span class="js-stale-session-flash-signed-out" hidden>You signed out in another tab or window. <a href="">Reload</a> to refresh your session.</span>
  </div>
  <template id="site-details-dialog">
  <details class="details-reset details-overlay details-overlay-dark lh-default text-gray-dark hx_rsm" open>
    <summary role="button" aria-label="Close dialog"></summary>
    <details-dialog class="Box Box--overlay d-flex flex-column anim-fade-in fast hx_rsm-dialog hx_rsm-modal">
      <button class="Box-btn-octicon m-0 btn-octicon position-absolute right-0 top-0" type="button" aria-label="Close dialog" data-close-dialog>
        <svg class="octicon octicon-x" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path fill-rule="evenodd" d="M3.72 3.72a.75.75 0 011.06 0L8 6.94l3.22-3.22a.75.75 0 111.06 1.06L9.06 8l3.22 3.22a.75.75 0 11-1.06 1.06L8 9.06l-3.22 3.22a.75.75 0 01-1.06-1.06L6.94 8 3.72 4.78a.75.75 0 010-1.06z"></path></svg>
      </button>
      <div class="octocat-spinner my-6 js-details-dialog-spinner"></div>
    </details-dialog>
  </details>
</template>

  <div class="Popover js-hovercard-content position-absolute" style="display: none; outline: none;" tabindex="0">
  <div class="Popover-message Popover-message--bottom-left Popover-message--large Box box-shadow-large" style="width:360px;">
  </div>
</div>


  </body>
</html>

