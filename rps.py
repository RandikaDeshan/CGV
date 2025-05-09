def _init_(self):
    # Game state
    self.state = "waiting"  # "waiting", "countdown", "playing", "result"
    self.countdown_start = 0
    self.countdown_duration = 3
    self.user_gesture = None
    self.computer_gesture = None
    self.result = None
    self.score = {"user": 0, "computer": 0, "ties": 0}
                  def start_game(self):
    self.state = "countdown"
    self.countdown_start = time.time()
    self.status_label.config(text="Get Ready!")
    self.instruction_label.config(text="Show your gesture on 'Shoot!'")
    self.start_button.config(state="disabled")

def update(self):
    ret, frame = self.cap.read()
    
    if ret:
        # Flip frame horizontally for a more natural view
        frame = cv2.flip(frame, 1)
        
        # Process frame
        processed_frame, gesture = self.process_frame(frame)
        
        # State machine for game flow
        if self.state == "countdown":
            elapsed = time.time() - self.countdown_start
            if elapsed < self.countdown_duration:
                count = self.countdown_duration - int(elapsed)
 self.status_label.config(text=f"Get Ready! {count}")
                
                # Draw countdown on frame
                cv2.putText(processed_frame, str(count), (frame.shape[1]//2 - 50, frame.shape[0]//2), 
                            cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 0, 255), 8)
            else:
                self.state = "playing"
                self.status_label.config(text="Rock, Paper, Scissors, Shoot!")
                
                # Show instruction for a brief moment
                cv2.putText(processed_frame, "SHOOT!", (frame.shape[1]//2 - 150, frame.shape[0]//2), 
                            cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 6)
                
                # Schedule to capture and process result in 1 second
                self.root.after(1000, self.capture_result)
        
        elif self.state == "playing":
            if gesture:
                self.user_gesture = gesture
                # This will be handled by capture_result
        
        elif self.state == "result":
            # Display result overlay
            self.display_result_overlay(processed_frame)
            def capture_result(self):
    if self.state == "playing":
        # Determine computer's gesture
        choices = ["rock", "paper", "scissors"]
        self.computer_gesture = random.choice(choices)
        
        # Determine winner
        if self.user_gesture in choices:
            self.result = self.determine_winner(self.user_gesture, self.computer_gesture)
            
            # Update score
            if self.result == "You Win!":
                self.score["user"] += 1
            elif self.result == "Computer Wins!":
                self.score["computer"] += 1
            else:  # Tie
                self.score["ties"] += 1
            
            self.update_score_display()
        else:
            self.result = "Invalid gesture"
            self.user_gesture = "unknown"
        
        # Update labels
        self.user_choice_label.config(text=self.user_gesture.capitalize())
        self.computer_choice_label.config(text=self.computer_gesture.capitalize())
        self.result_label.config(text=self.result)

        # Update status
        self.status_label.config(text="Game Result")
        self.instruction_label.config(text="Press 'Start Game' to play again")
        
        # Change state
        self.state = "result"
        
        # Re-enable the start button after 2 seconds
        self.root.after(2000, lambda: self.start_button.config(state="normal"))

def determine_winner(self, user_gesture, computer_gesture):
    if user_gesture == computer_gesture:
        return "Tie!"
    elif (user_gesture == "rock" and computer_gesture == "scissors") or \
         (user_gesture == "scissors" and computer_gesture == "paper") or \
         (user_gesture == "paper" and computer_gesture == "rock"):
        return "You Win!"
    else:
        return "Computer Wins!"