document.getElementById("nav").innerHTML = `
  <aside class="sidebar" id="sidebar">

    <div class="sidebar-top">
        <button class="toggle-btn" onclick="toggleSidebar()">◄◄</button>
    </div>

      <hr class="sidebar-divider" />

    <div>
        <label>
          <input type="checkbox" id="darkToggle" onchange="toggleDarkMode()"> Dark mode
        </label>
      </div>

      <hr class="sidebar-divider" />

      <nav>
        <div class="section">
          <div class="section-toggle" onclick="toggleSection(this)">Introduction ▸</div>
          <div class="sub-links">
            <a href="user_guide.html#overview">Overview</a>
            <a href="user_guide.html#requirements">Requirements</a>
            <a href="user_guide.html#installation">Installation</a>
          </div>

          <div class="section-toggle" onclick="toggleSection(this)">Basic Usage ▸</div>
          <div class="sub-links">
            <a href="general_guide.html#general">Opening pgn files</a>
          </div>
          
          <div class="section-toggle" onclick="toggleSection(this)">pgn-extract arguments ▸</div>
          <div class="sub-links">
            <a href="filters.html">Filter Commands</a>
            <a href="#outputs">Output Commands</a>
          </div>

          <div class="section-toggle" onclick="toggleSection(this)">Changelog ▸</div>
          <div class="sub-links">
            <a href="#subsection">July 2025</a>
            <a href="#subsection">June 2025</a>
            <a href="#subsection">May 2025</a>
          </div>

        </div>
      </nav>
    </aside>

    <!-- Reopen Sidebar Button -->
    <button class="reopen-btn" onclick="toggleSidebar()" id="reopenBtn">☰</button>
    `;