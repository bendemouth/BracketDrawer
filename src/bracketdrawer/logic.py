import matplotlib.pyplot as plt

class BracketDrawer:
    def __init__(self, tournament_size):
        try:
            self.team_height = 1.0
            self.round_width = 4.0
            self.text_offset = 0.0
            self.tournament_size = tournament_size
            if tournament_size % 4 != 0:
                raise ValueError("Tournament size must be divisible by 4 in order to get proper quadrants")
            self.matchup_pairs = self.get_seed_pairs(self.tournament_size)
        except ValueError as e:
            print(f"Error: {e}")
            raise
            

    def draw_bracket(self, left_teams, right_teams, **kwargs):
        """
        Main draw bracket method

        Args:
            left_teams(list): list of team labels for the left bracket
            right_teams(list): list of team labels for the right bracket
        
            **kwargs:
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

        title = kwargs.get('title', "")
        logo_path = kwargs.get('logo_path', "")
        subtitle_left = kwargs.get('subtitle_left', "")
        subtitle_right = kwargs.get('subtitle_right', "")
        social_handle = kwargs.get('social_handle', "")
        website = kwargs.get('website', "")

        fig_height = ((len(left_teams) + len(right_teams)) / 2) * self.team_height + 2
        fig_width = 30
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(fig_width, fig_height))
        
        # Split each region's teams into top and bottom halves
        # Assumes teams are already in proper seed order
        left_top = left_teams[:len(left_teams)//2]
        left_bottom = left_teams[len(left_teams)//2:]
        right_top = right_teams[:len(right_teams)//2]
        right_bottom = right_teams[len(right_teams)//2:]
        
        # Left bracket: left top, right bottom
        left_bracket = left_top + right_bottom
        
        # Right bracket: right top, left bottom
        right_bracket = right_top + left_bottom
        
        # Draw left bracket (pointing right)
        self._draw_sub_bracket(ax1, left_bracket, title=subtitle_left, direction=1)
        
        # Draw right bracket (pointing left)
        self._draw_sub_bracket(ax2, right_bracket, title=subtitle_right, direction=-1)
        
        plt.subplots_adjust(wspace=-0.2) #Brings bracket sides closer together
        fig.suptitle(title, fontsize=20) #Set title argument as super title

        # Add logo
        if logo_path:
            logo_img = plt.imread(logo_path)
            # Create a new axes for the logo
            logo_ax = fig.add_axes([0.42, 0.32, 0.15, 0.15])  # [left, bottom, width, height]
            logo_ax.imshow(logo_img)
            logo_ax.axis('off')

        # Add social media handle and website
        footer = []

        if social_handle:
            footer.append(social_handle)

        if website:
            footer.append(website)

        if footer:
            fig.text(0.95, 0.02, " | ".join(footer), 
                    horizontalalignment='right',
                    verticalalignment='bottom',
                    fontsize=10.5,
                    style='italic',
                    color='black')
            
        return fig
    def _draw_sub_bracket(self, ax, teams, title, direction=1):
        """
        Helper method for main draw_bracket method

        Args:
            ax(matplotlib axes object): matplotlib axes object
            teams(list): list of team labels
            title(str): string for the title, will serve as subtitle for full bracket
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
        ax.set_title(title, fontsize=12)
        
        # Draw initial team positions
        positions = []
        for i, team in enumerate(teams):
            y = (num_teams - i - 0.5) * self.team_height
            
            # Set starting x position based on direction
            x_start = 0 if direction == 1 else self.round_width * num_rounds
            positions.append((x_start, y))
            
            # Draw the horizontal line and text
            if direction == 1:
                ax.plot([-2.5, 0], [y, y], 'k-', linewidth=1)  # left bracket first round line length 
                ax.text(-0.5, y + 0.1, team, ha='center', va='center', fontsize=10.5, family='monospace', fontweight='bold') # left bracket first round text position
            else:
                ax.plot([self.round_width * num_rounds, self.round_width * num_rounds + 2.5], [y, y], 'k-', linewidth=1)  # right bracket first round line length
                ax.text(self.round_width * num_rounds + 0.5, y + 0.1, team, ha='center', va='center', fontsize=10.5, family='monospace', fontweight='bold') # right bracket first round text position

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
        Get first round paired matchups and applies seeds, labels.

        Args:
            df(DataFrame): dataframe of teams
            swap_teams(tuple): tuple of seeds to swap if needed
            append(str): string to append to the team labels. (Ex. "North" or "South")

        Returns:
            List of paired teams in order for the first round
        """
        ordered_teams = []
        # Create a copy of the dataframe to avoid modifying the original
        df_copy = df.copy()

        # Add seed column
        df_copy['seed'] = range(1, len(df_copy) + 1)

        if append:
            # Add team label column
            df_copy['team_label'] = "#" + df_copy['seed'].astype(str) + " " + append + " - " + df_copy['Team']
        else:
            # Add team label column
            df_copy['team_label'] = "#" + df_copy['seed'].astype(str) + " - " + df_copy['Team']
        
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
    

    def get_seed_pairs(self, tournament_size):
        """
        Get matchup pairs for the tournament
        """
        pairs = []

        for i in range(1, tournament_size // 2 + 1):
            pairs.append((i, tournament_size + 1 - i))

        return pairs
