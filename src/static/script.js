// Global variables
let teams = [];
let players = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadTeams();
    loadPlayers();
});

// Tab functionality
function showTab(tabName) {
    // Hide all tab panes
    const tabPanes = document.querySelectorAll('.tab-pane');
    tabPanes.forEach(pane => pane.classList.remove('active'));
    
    // Remove active class from all tabs
    const tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Show selected tab pane
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to clicked tab
    event.target.classList.add('active');
}

// API helper function
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(`/api/analysis${endpoint}`, options);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Load teams for dropdowns
async function loadTeams() {
    try {
        const response = await apiCall('/teams');
        teams = response.teams;
        
        // Populate all team dropdowns
        const teamSelects = ['team-select', 'team1-select', 'team2-select'];
        teamSelects.forEach(selectId => {
            const select = document.getElementById(selectId);
            if (select) {
                select.innerHTML = '<option value="">Bitte wählen...</option>';
                teams.forEach(team => {
                    const option = document.createElement('option');
                    option.value = team;
                    option.textContent = team;
                    select.appendChild(option);
                });
            }
        });
    } catch (error) {
        console.error('Failed to load teams:', error);
    }
}

// Load players for dropdowns
async function loadPlayers() {
    try {
        const response = await apiCall('/players');
        players = response.players;
        
        // Populate all player dropdowns
        const playerSelects = ['player-select', 'player1-select', 'player2-select'];
        playerSelects.forEach(selectId => {
            const select = document.getElementById(selectId);
            if (select) {
                select.innerHTML = '<option value="">Bitte wählen...</option>';
                players.forEach(player => {
                    const option = document.createElement('option');
                    option.value = player;
                    option.textContent = player;
                    select.appendChild(option);
                });
            }
        });
    } catch (error) {
        console.error('Failed to load players:', error);
    }
}

// Load overview data
async function loadOverview() {
    const resultsDiv = document.getElementById('overview-results');
    resultsDiv.innerHTML = '<div class="loading">Lade Daten...</div>';
    
    try {
        const response = await apiCall('/overview');
        
        const html = `
            <div class="results">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">${response.statistics.total_injuries}</div>
                        <div class="stat-label">Gesamte Verletzungen</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${response.statistics.average_days_out.toFixed(1)}</div>
                        <div class="stat-label">Ø Ausfalltage</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${response.statistics.total_games_missed}</div>
                        <div class="stat-label">Verpasste Spiele</div>
                    </div>
                </div>
                
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Spieler</th>
                            <th>Team</th>
                            <th>Verletzung</th>
                            <th>Saison</th>
                            <th>Ausfalltage</th>
                            <th>Verpasste Spiele</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${response.data.map(injury => `
                            <tr>
                                <td>${injury.Spieler}</td>
                                <td>${injury.Team}</td>
                                <td>${injury.Verletzung}</td>
                                <td>${injury.Saison}</td>
                                <td>${injury.Ausfalltage}</td>
                                <td>${injury.Spiele_verpasst}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        resultsDiv.innerHTML = html;
    } catch (error) {
        resultsDiv.innerHTML = '<div class="error">Fehler beim Laden der Daten: ' + error.message + '</div>';
    }
}

// Analyze team
async function analyzeTeam() {
    const teamSelect = document.getElementById('team-select');
    const teamName = teamSelect.value;
    const resultsDiv = document.getElementById('team-results');
    
    if (!teamName) {
        resultsDiv.innerHTML = '<div class="error">Bitte wählen Sie ein Team aus.</div>';
        return;
    }
    
    resultsDiv.innerHTML = '<div class="loading">Analysiere Team...</div>';
    
    try {
        const response = await apiCall(`/team/${encodeURIComponent(teamName)}`);
        
        const html = `
            <div class="results">
                <h3>Analyse für ${response.team}</h3>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">${response.statistics.total_injuries}</div>
                        <div class="stat-label">Gesamte Verletzungen</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${response.statistics.average_days_out.toFixed(1)}</div>
                        <div class="stat-label">Ø Ausfalltage</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${response.statistics.total_games_missed}</div>
                        <div class="stat-label">Verpasste Spiele</div>
                    </div>
                </div>
                
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Spieler</th>
                            <th>Verletzung</th>
                            <th>Saison</th>
                            <th>Ausfalltage</th>
                            <th>Verpasste Spiele</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${response.data.map(injury => `
                            <tr>
                                <td>${injury.Spieler}</td>
                                <td>${injury.Verletzung}</td>
                                <td>${injury.Saison}</td>
                                <td>${injury.Ausfalltage}</td>
                                <td>${injury.Spiele_verpasst}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        resultsDiv.innerHTML = html;
    } catch (error) {
        resultsDiv.innerHTML = '<div class="error">Fehler beim Analysieren des Teams: ' + error.message + '</div>';
    }
}

// Analyze player
async function analyzePlayer() {
    const playerSelect = document.getElementById('player-select');
    const playerName = playerSelect.value;
    const resultsDiv = document.getElementById('player-results');
    
    if (!playerName) {
        resultsDiv.innerHTML = '<div class="error">Bitte wählen Sie einen Spieler aus.</div>';
        return;
    }
    
    resultsDiv.innerHTML = '<div class="loading">Analysiere Spieler...</div>';
    
    try {
        const response = await apiCall(`/player/${encodeURIComponent(playerName)}`);
        
        const html = `
            <div class="results">
                <h3>Analyse für ${response.player}</h3>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">${response.statistics.total_injuries}</div>
                        <div class="stat-label">Gesamte Verletzungen</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${response.statistics.average_days_out.toFixed(1)}</div>
                        <div class="stat-label">Ø Ausfalltage</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${response.statistics.total_games_missed}</div>
                        <div class="stat-label">Verpasste Spiele</div>
                    </div>
                </div>
                
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Team</th>
                            <th>Verletzung</th>
                            <th>Saison</th>
                            <th>Ausfalltage</th>
                            <th>Verpasste Spiele</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${response.data.map(injury => `
                            <tr>
                                <td>${injury.Team}</td>
                                <td>${injury.Verletzung}</td>
                                <td>${injury.Saison}</td>
                                <td>${injury.Ausfalltage}</td>
                                <td>${injury.Spiele_verpasst}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        resultsDiv.innerHTML = html;
    } catch (error) {
        resultsDiv.innerHTML = '<div class="error">Fehler beim Analysieren des Spielers: ' + error.message + '</div>';
    }
}

// Show compare type
function showCompareType(type) {
    document.getElementById('compare-teams').style.display = type === 'teams' ? 'block' : 'none';
    document.getElementById('compare-players').style.display = type === 'players' ? 'block' : 'none';
    document.getElementById('compare-results').innerHTML = '';
}

// Compare teams
async function compareTeams() {
    const team1 = document.getElementById('team1-select').value;
    const team2 = document.getElementById('team2-select').value;
    const resultsDiv = document.getElementById('compare-results');
    
    if (!team1 || !team2) {
        resultsDiv.innerHTML = '<div class="error">Bitte wählen Sie beide Teams aus.</div>';
        return;
    }
    
    resultsDiv.innerHTML = '<div class="loading">Vergleiche Teams...</div>';
    
    try {
        const response = await apiCall('/compare/teams', 'POST', { team1, team2 });
        
        const html = `
            <div class="results">
                <h3>Team-Vergleich</h3>
                <div class="comparison-grid">
                    <div class="comparison-card">
                        <div class="comparison-title">${response.team1.name}</div>
                        <div class="stats-grid">
                            <div class="stat-card">
                                <div class="stat-number">${response.team1.total_injuries}</div>
                                <div class="stat-label">Verletzungen</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-number">${response.team1.average_days_out.toFixed(1)}</div>
                                <div class="stat-label">Ø Ausfalltage</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-number">${response.team1.total_games_missed}</div>
                                <div class="stat-label">Verpasste Spiele</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="comparison-card">
                        <div class="comparison-title">${response.team2.name}</div>
                        <div class="stats-grid">
                            <div class="stat-card">
                                <div class="stat-number">${response.team2.total_injuries}</div>
                                <div class="stat-label">Verletzungen</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-number">${response.team2.average_days_out.toFixed(1)}</div>
                                <div class="stat-label">Ø Ausfalltage</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-number">${response.team2.total_games_missed}</div>
                                <div class="stat-label">Verpasste Spiele</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        resultsDiv.innerHTML = html;
    } catch (error) {
        resultsDiv.innerHTML = '<div class="error">Fehler beim Vergleichen der Teams: ' + error.message + '</div>';
    }
}

// Compare players
async function comparePlayers() {
    const player1 = document.getElementById('player1-select').value;
    const player2 = document.getElementById('player2-select').value;
    const resultsDiv = document.getElementById('compare-results');
    
    if (!player1 || !player2) {
        resultsDiv.innerHTML = '<div class="error">Bitte wählen Sie beide Spieler aus.</div>';
        return;
    }
    
    resultsDiv.innerHTML = '<div class="loading">Vergleiche Spieler...</div>';
    
    try {
        const response = await apiCall('/compare/players', 'POST', { player1, player2 });
        
        const html = `
            <div class="results">
                <h3>Spieler-Vergleich</h3>
                <div class="comparison-grid">
                    <div class="comparison-card">
                        <div class="comparison-title">${response.player1.name}</div>
                        <div class="stats-grid">
                            <div class="stat-card">
                                <div class="stat-number">${response.player1.total_injuries}</div>
                                <div class="stat-label">Verletzungen</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-number">${response.player1.average_days_out.toFixed(1)}</div>
                                <div class="stat-label">Ø Ausfalltage</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-number">${response.player1.total_games_missed}</div>
                                <div class="stat-label">Verpasste Spiele</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="comparison-card">
                        <div class="comparison-title">${response.player2.name}</div>
                        <div class="stats-grid">
                            <div class="stat-card">
                                <div class="stat-number">${response.player2.total_injuries}</div>
                                <div class="stat-label">Verletzungen</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-number">${response.player2.average_days_out.toFixed(1)}</div>
                                <div class="stat-label">Ø Ausfalltage</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-number">${response.player2.total_games_missed}</div>
                                <div class="stat-label">Verpasste Spiele</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        resultsDiv.innerHTML = html;
    } catch (error) {
        resultsDiv.innerHTML = '<div class="error">Fehler beim Vergleichen der Spieler: ' + error.message + '</div>';
    }
}

