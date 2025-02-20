import matplotlib.pyplot as plt

class BracketGenerator:
    def __init__(self, class_size):
        self.team_height = 1.0
        self.round_width = 4.0
        self.text_offset = 0.0
        self.class_size = class_size
        self.matchup_pairs = self.get_seed_pairs(self.class_size)

            

    def draw_bracket(self, left_teams, right_teams, title="", logo_path="", subtitle_left="", subtitle_right="", social_handle="", website=""):
        """
        Main draw bracket method

        Args:
            left_teams(list): list of team labels for the left bracket
            right_teams(list): list of team labels for the right bracket
            title(str): string for the title
            logo_path(str): image path for a logo to add to the middle of the bracket
            subtitle_left(str): string for the left bracket subtitle
            subtitle_right(str): string for the right bracket subtitle
            social_handle(str): string for the social handle to display in corner
            website(str): string for the website in corner

        Returns:
            fig: matplotlib figure object

        Notes:
            This will order teams in the order that they are provided in the left_teams and right_teams arguments, 
            and split them into top and bottom halves so that they are on opposite sides of the bracket.
        """
        total_teams = len(left_teams)
        fig_height = total_teams * self.team_height + 2
        fig_width = 30
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(fig_width, fig_height))
        
        # Split each region's teams into top and bottom halves
        if self.class_size == 32:   
            # Assumes teams are already in proper seed order
            north_top = left_teams[:8]      # Teams 1,16,8,9,4,13,5,12
            north_bottom = left_teams[8:]    # Teams 3,14,6,11,7,10,2,15
            south_top = right_teams[:8]       # Teams 1,16,8,9,4,13,5,12
            south_bottom = right_teams[8:]    # Teams 3,14,6,11,7,10,2,15
        elif self.class_size == 16:
            north_top = left_teams[:4]
            north_bottom = left_teams[4:]
            south_top = right_teams[:4]
            south_bottom = right_teams[4:]
        
        # Left bracket: North top, South bottom
        left_bracket = north_top + south_bottom
        
        # Right bracket: South top, North bottom
        right_bracket = south_top + north_bottom
        
        # Draw left bracket (pointing right)
        self._draw_sub_bracket(ax1, left_bracket, subtitle_left, direction=1)
        
        # Draw right bracket (pointing left)
        self._draw_sub_bracket(ax2, right_bracket, subtitle_right, direction=-1)
        
        plt.subplots_adjust(wspace=-0.2) #Brings bracket sides closer together
        fig.suptitle(title, fontsize=20) #Set title argument as super title

        # Add logo
        if logo_path:
            logo_img = plt.imread(logo_path)
            # Create a new axes for the logo
            logo_ax = fig.add_axes([0.42, 0.32, 0.15, 0.15])  # [left, bottom, width, height]
            logo_ax.imshow(logo_img)
            logo_ax.axis('off')

        # Add twitter handle and website
        if social_handle and website:
            fig.text(0.95, 0.02, f"{social_handle} | {website}", 
                    horizontalalignment='right',
                    verticalalignment='bottom',
                    fontsize=10.5,
                    style='italic',
                    color='black')

        return fig

    def _draw_sub_bracket(self, ax, teams, subtitle, direction=1):
        """
        Helper method for main draw_bracket method

        Args:
            ax(matplotlib axes object): matplotlib axes object
            teams(list): list of team labels
            subtitle(str): string for the subtitle
            direction(int): 1 for right, -1 for left

        Returns:
            fig: matplotlib figure object
        """
        num_teams = len(teams)
        num_rounds = (num_teams - 1).bit_length()
        
        # Setup the subplot
        ax.set_xlim(-2, self.round_width * (num_rounds + 1))
        ax.set_ylim(-1, num_teams * self.team_height + 1)
        ax.axis('off')
        ax.set_title(subtitle, fontsize=12)
        
        # Draw initial team positions
        positions = []
        for i, team in enumerate(teams):
            y = (num_teams - i - 0.5) * self.team_height
            
            # Set starting x position based on direction
            x_start = 0 if direction == 1 else self.round_width * num_rounds
            positions.append((x_start, y))
            
            # Draw the horizontal line and text
            if direction == 1:
                ax.plot([-2.5, 0], [y, y], 'k-', linewidth=1)  # North bracket first round line length 
                ax.text(-0.5, y + 0.1, team, ha='center', va='center', fontsize=10.5, family='monospace', fontweight='bold') # North bracket first round text position
            else:
                ax.plot([self.round_width * num_rounds, self.round_width * num_rounds + 2.5], [y, y], 'k-', linewidth=1)  # South bracket first round line length
                ax.text(self.round_width * num_rounds + 0.5, y + 0.1, team, ha='center', va='center', fontsize=10.5, family='monospace', fontweight='bold') # South bracket first round text position

        # Draw rounds
        for round_num in range(num_rounds):
            next_positions = []
            
            for i in range(0, len(positions), 2):
                if i + 1 < len(positions):
                    x1, y1 = positions[i]
                    x2, y2 = positions[i + 1]
                    
                    next_x = x1 + (self.round_width * direction)
                    connector_x = x1 + (self.round_width/3 * direction)
                    next_y = (y1 + y2) / 2
                    next_positions.append((next_x, next_y))
                    
                    # Draw connecting lines
                    ax.plot([x1, connector_x], [y1, y1], 'k-', linewidth=1)
                    ax.plot([x2, connector_x], [y2, y2], 'k-', linewidth=1)
                    ax.plot([connector_x, connector_x], [min(y1, y2), max(y1, y2)], 'k-', linewidth=1)
                    ax.plot([connector_x, next_x], [next_y, next_y], 'k-', linewidth=1)
                else:
                    next_x = x1 + (self.round_width * direction)
                    next_positions.append((next_x, y1))
            
            positions = next_positions

    def get_tournament_seeds(self, df, swap_teams=None, append = ""):
        """
        Get first round paired matchups

        Args:
            df(DataFrame): dataframe of teams
            swap_teams(tuple): tuple of seeds to swap if needed
            append(str): string to append to the team labels

        Returns:
            List of paired teams in order for the first round
        """
        ordered_teams = []
        # Create a copy of the dataframe to avoid modifying the original
        df_copy = df.copy()

        # Add seed column
        df_copy['seed'] = range(1, len(df_copy) + 1)

        # Add team label column
        df_copy['team_label'] = "#" + df_copy['seed'].astype(str) + " " + append + " - " + df_copy['Team']
        
        # If swap_teams is provided, swap the specified seeds
        if swap_teams:
            seed1, seed2 = swap_teams
            # Swap the team_labels for the specified seeds
            temp = df_copy.loc[df_copy['seed'] == seed1, 'team_label'].iloc[0]
            df_copy.loc[df_copy['seed'] == seed1, 'team_label'] = df_copy.loc[df_copy['seed'] == seed2, 'team_label'].iloc[0]
            df_copy.loc[df_copy['seed'] == seed2, 'team_label'] = temp
        
        for seed1, seed2 in self.matchup_pairs:
            # Get teams for each matchup
            team1 = df_copy[df_copy['seed'] == seed1]['team_label'].iloc[0]
            team2 = df_copy[df_copy['seed'] == seed2]['team_label'].iloc[0]
            ordered_teams.extend([team1, team2])

        return ordered_teams
    

    def get_seed_pairs(self, class_size):
        """
        Get matchup pairs for the tournament
        """
        if class_size == 32:
            return [(1, 16), (8, 9), (4, 13), (5, 12), (3, 14), (6, 11), (7, 10), (2, 15)]
        elif class_size == 16:
            return [(1, 8), (4, 5), (3, 6), (2, 7)]
