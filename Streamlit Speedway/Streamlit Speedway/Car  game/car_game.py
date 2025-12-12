import streamlit as st
import random
import time
from PIL import Image, ImageDraw
import io
import base64


class CarGame:
    def __init__(self, width=400, height=600):
        self.width = width
        self.height = height
        self.reset_game()
    
    def reset_game(self):
        # Player car
        self.player_x = self.width // 2
        self.player_y = self.height - 100
        self.player_speed = 0
        self.player_lives = 3
        
        # Game state
        self.score = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        
        # Obstacles
        self.obstacles = []
        self.obstacle_speed = 3
        
        # Collectibles
        self.coins = []
        self.coin_speed = 2
        
        # Road lines for visual effect
        self.road_lines = []
        for i in range(0, self.height, 50):
            self.road_lines.append(i)
    
    def move_player(self, direction):
        """Move player car left or right"""
        if direction == "left" and self.player_x > 50:
            self.player_x -= 5
        elif direction == "right" and self.player_x < self.width - 50:
            self.player_x += 5
    
    def update_obstacles(self):
        """Update obstacle positions and create new ones"""
        # Move existing obstacles
        for obstacle in self.obstacles[:]:
            obstacle['y'] += self.obstacle_speed
            if obstacle['y'] > self.height:
                self.obstacles.remove(obstacle)
                self.score += 10
        
        # Create new obstacles
        if random.random() < 0.02:  # 2% chance each frame
            obstacle = {
                'x': random.randint(50, self.width - 50),
                'y': -50,
                'width': random.randint(30, 60),
                'height': random.randint(20, 40),
                'type': random.choice(['car', 'truck', 'barrier'])
            }
            self.obstacles.append(obstacle)
    
    def update_coins(self):
        """Update coin positions and create new ones"""
        # Move existing coins
        for coin in self.coins[:]:
            coin['y'] += self.coin_speed
            if coin['y'] > self.height:
                self.coins.remove(coin)
        
        # Create new coins
        if random.random() < 0.01:  # 1% chance each frame
            coin = {
                'x': random.randint(50, self.width - 50),
                'y': -30,
                'size': random.randint(8, 15)
            }
            self.coins.append(coin)
    
    def update_road_lines(self):
        """Update road line positions for scrolling effect"""
        for i, line_y in enumerate(self.road_lines):
            self.road_lines[i] += self.obstacle_speed
            if self.road_lines[i] > self.height:
                self.road_lines[i] = -50
    
    def check_collisions(self):
        """Check for collisions between player and obstacles/coins"""
        player_rect = {
            'left': self.player_x - 20,
            'right': self.player_x + 20,
            'top': self.player_y - 30,
            'bottom': self.player_y + 30
        }
        
        # Check obstacle collisions
        for obstacle in self.obstacles:
            obstacle_rect = {
                'left': obstacle['x'] - obstacle['width']//2,
                'right': obstacle['x'] + obstacle['width']//2,
                'top': obstacle['y'] - obstacle['height']//2,
                'bottom': obstacle['y'] + obstacle['height']//2
            }
            
            if (player_rect['left'] < obstacle_rect['right'] and
                player_rect['right'] > obstacle_rect['left'] and
                player_rect['top'] < obstacle_rect['bottom'] and
                player_rect['bottom'] > obstacle_rect['top']):
                self.player_lives -= 1
                self.obstacles.remove(obstacle)
                if self.player_lives <= 0:
                    self.game_over = True
        
        # Check coin collisions
        for coin in self.coins[:]:
            coin_rect = {
                'left': coin['x'] - coin['size'],
                'right': coin['x'] + coin['size'],
                'top': coin['y'] - coin['size'],
                'bottom': coin['y'] + coin['size']
            }
            
            if (player_rect['left'] < coin_rect['right'] and
                player_rect['right'] > coin_rect['left'] and
                player_rect['top'] < coin_rect['bottom'] and
                player_rect['bottom'] > coin_rect['top']):
                self.coins.remove(coin)
                self.score += 50
    
    def update_level(self):
        """Increase level and difficulty based on score"""
        new_level = (self.score // 500) + 1
        if new_level > self.level:
            self.level = new_level
            self.obstacle_speed += 0.5
            self.coin_speed += 0.3
    
    def update(self):
        """Update game state"""
        if self.game_over or self.paused:
            return
        
        self.update_obstacles()
        self.update_coins()
        self.update_road_lines()
        self.check_collisions()
        self.update_level()

def create_game_image(game, cell_size=2):
    """Create a visual representation of the game"""
    width = game.width // cell_size
    height = game.height // cell_size
    
    # Create image with dark background
    img = Image.new('RGB', (width, height), '#1a1a1a')
    draw = ImageDraw.Draw(img)
    
    # Draw road
    road_color = '#404040'
    road_width = width // 3
    road_x = (width - road_width) // 2
    draw.rectangle([road_x, 0, road_x + road_width, height], fill=road_color)
    
    # Draw road lines
    line_color = '#ffffff'
    line_width = 3
    for line_y in game.road_lines:
        line_y_scaled = line_y // cell_size
        if 0 <= line_y_scaled < height:
            draw.rectangle([road_x + road_width//2 - line_width//2, line_y_scaled,
                           road_x + road_width//2 + line_width//2, line_y_scaled + 20],
                          fill=line_color)
    
    # Draw player car
    player_color = '#00ff00'
    player_x_scaled = game.player_x // cell_size
    player_y_scaled = game.player_y // cell_size
    draw.rectangle([player_x_scaled - 15, player_y_scaled - 20,
                   player_x_scaled + 15, player_y_scaled + 20], fill=player_color)
    
    # Draw car details
    draw.rectangle([player_x_scaled - 10, player_y_scaled - 15,
                   player_x_scaled + 10, player_y_scaled - 5], fill='#ffffff')
    draw.rectangle([player_x_scaled - 10, player_y_scaled + 5,
                   player_x_scaled + 10, player_y_scaled + 15], fill='#ffffff')
    
    # Draw obstacles
    for obstacle in game.obstacles:
        obstacle_x = obstacle['x'] // cell_size
        obstacle_y = obstacle['y'] // cell_size
        obstacle_w = obstacle['width'] // cell_size
        obstacle_h = obstacle['height'] // cell_size
        
        if obstacle['type'] == 'car':
            color = '#ff0000'
        elif obstacle['type'] == 'truck':
            color = '#ff6600'
        else:
            color = '#ffff00'
        
        draw.rectangle([obstacle_x - obstacle_w//2, obstacle_y - obstacle_h//2,
                       obstacle_x + obstacle_w//2, obstacle_y + obstacle_h//2], fill=color)
    
    # Draw coins
    coin_color = '#ffff00'
    for coin in game.coins:
        coin_x = coin['x'] // cell_size
        coin_y = coin['y'] // cell_size
        coin_size = coin['size'] // cell_size
        
        # Draw coin as circle
        draw.ellipse([coin_x - coin_size, coin_y - coin_size,
                     coin_x + coin_size, coin_y + coin_size], fill=coin_color)
    
    return img

def image_to_base64(img):
    """Convert PIL image to base64 string for Streamlit"""
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

def main():
    st.set_page_config(
        page_title="Car Racing Game",
        page_icon="🏎️",
        layout="wide"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #ff6b6b;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .game-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    .game-display {
        background-color: #000000;
        padding: 1rem;
        border-radius: 10px;
        border: 3px solid #333333;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stats-container {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }
    .control-button {
        background: linear-gradient(45deg, #ff6b6b, #ee5a24);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-size: 1.1rem;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s;
        margin: 0.25rem;
    }
    .control-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">🏎️ Car Racing Game</h1>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'game' not in st.session_state:
        st.session_state.game = CarGame()
    if 'last_update' not in st.session_state:
        st.session_state.last_update = time.time()
    if 'high_score' not in st.session_state:
        st.session_state.high_score = 0
    
    # Sidebar controls
    st.sidebar.header("🎮 Game Controls")
    
    # Game settings
    game_speed = st.sidebar.slider("Game Speed", 0.05, 0.2, 0.1, 0.01)
    
    # Control buttons
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("⬅️ Left", key="left"):
            st.session_state.game.move_player("left")
            st.rerun()
    
    with col2:
        if st.button("➡️ Right", key="right"):
            st.session_state.game.move_player("right")
            st.rerun()
    
    col3, col4 = st.sidebar.columns(2)
    
    with col3:
        if st.button("⏸️ Pause", key="pause"):
            st.session_state.game.paused = not st.session_state.game.paused
            st.rerun()
    
    with col4:
        if st.button("🔄 Reset", key="reset"):
            st.session_state.game = CarGame()
            st.session_state.last_update = time.time()
            st.rerun()
    
    # Game status
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Game Status")
    
    # Update high score
    if st.session_state.game.score > st.session_state.high_score:
        st.session_state.high_score = st.session_state.game.score
    
    st.sidebar.metric("Score", st.session_state.game.score)
    st.sidebar.metric("High Score", st.session_state.high_score)
    st.sidebar.metric("Level", st.session_state.game.level)
    st.sidebar.metric("Lives", st.session_state.game.player_lives)
    
    if st.session_state.game.game_over:
        st.sidebar.error("💥 Game Over!")
    elif st.session_state.game.paused:
        st.sidebar.warning("⏸️ Game Paused")
    else:
        st.sidebar.success("🏁 Game Running")
    
    # Instructions
    st.sidebar.markdown("---")
    st.sidebar.subheader("📖 How to Play")
    st.sidebar.markdown("""
    - **⬅️➡️**: Move car left/right
    - **Avoid**: Red cars, orange trucks, yellow barriers
    - **Collect**: Yellow coins for bonus points
    - **Survive**: Don't hit obstacles!
    - **Level Up**: Score increases difficulty
    """)
    
    # Main game area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎮 Game Screen")
        
        # Game loop
        current_time = time.time()
        if (current_time - st.session_state.last_update > game_speed and 
            not st.session_state.game.game_over and not st.session_state.game.paused):
            st.session_state.game.update()
            st.session_state.last_update = current_time
        
        # Create and display game board
        game_img = create_game_image(st.session_state.game)
        
        # Convert to base64 and display
        img_base64 = image_to_base64(game_img)
        st.markdown(f"""
        <div class="game-display">
            <img src="data:image/png;base64,{img_base64}" style="max-width: 100%; height: auto;">
        </div>
        """, unsafe_allow_html=True)
        
        # Game over message
        if st.session_state.game.game_over:
            st.error("💥 Game Over! Press Reset to play again.")
        elif st.session_state.game.paused:
            st.warning("⏸️ Game Paused. Press Pause to resume.")
    
    with col2:
        st.subheader("📈 Game Statistics")
        
        # Player position
        st.write(f"**Player Position:** ({st.session_state.game.player_x}, {st.session_state.game.player_y})")
        
        # Obstacle count
        st.write(f"**Active Obstacles:** {len(st.session_state.game.obstacles)}")
        
        # Coin count
        st.write(f"**Active Coins:** {len(st.session_state.game.coins)}")
        
        # Game speed
        st.write(f"**Obstacle Speed:** {st.session_state.game.obstacle_speed:.1f}")
        st.write(f"**Coin Speed:** {st.session_state.game.coin_speed:.1f}")
        
        # Road lines
        st.write(f"**Road Lines:** {len(st.session_state.game.road_lines)}")
        
        # Game statistics
        st.subheader("🎯 Performance")
        st.write(f"**Current Level:** {st.session_state.game.level}")
        st.write(f"**Remaining Lives:** {st.session_state.game.player_lives}")
        
        # Obstacle types
        obstacle_types = {}
        for obstacle in st.session_state.game.obstacles:
            obstacle_types[obstacle['type']] = obstacle_types.get(obstacle['type'], 0) + 1
        
        if obstacle_types:
            st.write("**Obstacle Types:**")
            for obs_type, count in obstacle_types.items():
                st.write(f"  - {obs_type}: {count}")
    
    # Game features showcase
    with st.expander("✨ Game Features"):
        st.markdown("""
        - **🏎️ Car Racing**: Classic racing game mechanics
        - **🎯 Multiple Obstacles**: Cars, trucks, and barriers
        - **💰 Coin Collection**: Collect coins for bonus points
        - **📈 Progressive Difficulty**: Speed increases with level
        - **💚 Lives System**: Multiple lives for longer gameplay
        - **🏆 High Score**: Track your best performance
        - **🎨 Visual Effects**: Scrolling road and smooth graphics
        - **🎮 Responsive Controls**: Easy-to-use button controls
        """)
    
    # Tips and tricks
    with st.expander("💡 Tips & Tricks"):
        st.markdown("""
        ### 🎯 Scoring System:
        - **Avoiding Obstacles**: +10 points each
        - **Collecting Coins**: +50 points each
        - **Level Progression**: Every 500 points
        
        ### 🏁 Strategy Tips:
        - Stay in the center lane for better maneuverability
        - Prioritize avoiding obstacles over collecting coins
        - Watch for patterns in obstacle placement
        - Use quick taps for precise movement
        
        ### 🎮 Controls:
        - **Left/Right Buttons**: Move car horizontally
        - **Pause**: Stop the game temporarily
        - **Reset**: Start a new game
        - **Speed Slider**: Adjust game difficulty
        """)

if __name__ == "__main__":
    main() 