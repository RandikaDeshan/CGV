import cv2
import numpy as np
import time
import random
import mediapipe as mp
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

class RPSGame:

    def _init_(self):
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=False,
                                     max_num_hands=1,
                                     min_detection_confidence=0.5,
                                     min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils
    # Game state
        self.state = "waiting"  # "waiting", "countdown", "playing", "result"
        self.countdown_start = 0
        self.countdown_duration = 3
        self.user_gesture = None
        self.computer_gesture = None
        self.result = None
        self.score = {"user": 0, "computer": 0, "ties": 0}
        
        # Create output directory for processed images
        self.output_dir = "processed_images"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Setup GUI
        self.setup_gui()
        
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Rock Paper Scissors Game")
        self.root.geometry("1200x700")
        self.root.resizable(False, False)
        
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for camera feed
        self.left_panel = ttk.LabelFrame(main_frame, text="Camera Feed")
        self.left_panel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.camera_label = ttk.Label(self.left_panel)
        self.camera_label.pack(padx=10, pady=10)
        
        # Right panel for game info and processing steps
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Game status frame
        game_frame = ttk.LabelFrame(right_panel, text="Game Status")
        game_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.status_label = ttk.Label(game_frame, text="Say 'Rock, Paper, Scissors, Shoot!'", font=("Arial", 14))
        self.status_label.pack(pady=10)
        
        self.instruction_label = ttk.Label(game_frame, text="Press 'Start Game' to begin", font=("Arial", 12))
        self.instruction_label.pack(pady=5)
        
        # Results frame
        results_frame = ttk.Frame(game_frame)
        results_frame.pack(pady=10)
        
        ttk.Label(results_frame, text="You:", font=("Arial", 12)).grid(row=0, column=0, padx=5)
        self.user_choice_label = ttk.Label(results_frame, text="-", font=("Arial", 12))
        self.user_choice_label.grid(row=0, column=1, padx=5)
        
        ttk.Label(results_frame, text="Computer:", font=("Arial", 12)).grid(row=1, column=0, padx=5)
        self.computer_choice_label = ttk.Label(results_frame, text="-", font=("Arial", 12))
        self.computer_choice_label.grid(row=1, column=1, padx=5)
        
        ttk.Label(results_frame, text="Result:", font=("Arial", 12)).grid(row=2, column=0, padx=5)
        self.result_label = ttk.Label(results_frame, text="-", font=("Arial", 12))
        self.result_label.grid(row=2, column=1, padx=5)
        
        # Score frame
        score_frame = ttk.LabelFrame(game_frame, text="Score")
        score_frame.pack(pady=10, fill=tk.X)
        
        ttk.Label(score_frame, text="You:").grid(row=0, column=0, padx=10)
        self.user_score_label = ttk.Label(score_frame, text="0")
        self.user_score_label.grid(row=0, column=1, padx=10)
        
        ttk.Label(score_frame, text="Computer:").grid(row=0, column=2, padx=10)
        self.comp_score_label = ttk.Label(score_frame, text="0")
        self.comp_score_label.grid(row=0, column=3, padx=10)
        
        ttk.Label(score_frame, text="Ties:").grid(row=0, column=4, padx=10)
        self.ties_score_label = ttk.Label(score_frame, text="0")
        self.ties_score_label.grid(row=0, column=5, padx=10)
        
        # Button frame
        button_frame = ttk.Frame(game_frame)
        button_frame.pack(pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Game", command=self.start_game)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.reset_button = ttk.Button(button_frame, text="Reset Score", command=self.reset_score)
        self.reset_button.grid(row=0, column=1, padx=5)
        
        # Processing steps frame
        processing_frame = ttk.LabelFrame(right_panel, text="Image Processing Steps")
        processing_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.processing_canvas = tk.Canvas(processing_frame, height=300)
        self.processing_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure grid
        main_frame.columnconfigure(0, weight=3)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=1)
        
        # Initialize video capture
        self.cap = cv2.VideoCapture(0)
        
        # Store processing step images
        self.processing_images = []
        self.processing_photo_refs = []  # Keep references to prevent garbage collection
        
    def start_game(self):
        self.state = "countdown"
        self.countdown_start = time.time()
        self.status_label.config(text="Get Ready!")
        self.instruction_label.config(text="Show your gesture on 'Shoot!'")
        self.start_button.config(state="disabled")
        
    def reset_score(self):
        self.score = {"user": 0, "computer": 0, "ties": 0}
        self.update_score_display()
        
    def update_score_display(self):
        self.user_score_label.config(text=str(self.score["user"]))
        self.comp_score_label.config(text=str(self.score["computer"]))
        self.ties_score_label.config(text=str(self.score["ties"]))
        
    def detect_gesture(self, hand_landmarks):
        # Get fingertips and other landmarks
        landmarks = []
        for point in hand_landmarks.landmark:
            landmarks.append((point.x, point.y, point.z))
        
        # Check if fingers are extended
        # Thumb
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        thumb_extended = thumb_tip[0] < thumb_ip[0]  # For right hand
        
        # Other fingers
        finger_tips = [8, 12, 16, 20]  # Index, middle, ring, pinky
        finger_pips = [6, 10, 14, 18]  # Second joint of each finger
        
        extended_fingers = []
        for tip, pip in zip(finger_tips, finger_pips):
            extended_fingers.append(landmarks[tip][1] < landmarks[pip][1])
        
        # Determine gesture
        if all(extended_fingers) and thumb_extended:
            return "paper"
        elif not any(extended_fingers) and not thumb_extended:
            return "rock"
        elif extended_fingers[0] and extended_fingers[1] and not extended_fingers[2] and not extended_fingers[3]:
            return "scissors"
        else:
            return "unknown"
    
    def determine_winner(self, user_gesture, computer_gesture):
        if user_gesture == computer_gesture:
            return "Tie!"
        elif (user_gesture == "rock" and computer_gesture == "scissors") or \
             (user_gesture == "scissors" and computer_gesture == "paper") or \
             (user_gesture == "paper" and computer_gesture == "rock"):
            return "You Win!"
        else:
            return "Computer Wins!"
    
    def process_frame(self, frame):
        # Save original frame for display
        original_frame = frame.copy()
        
        # Clear previous processing images
        self.processing_images = []
        
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.processing_images.append(("RGB", rgb_frame.copy()))
        
        # Convert to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.processing_images.append(("Grayscale", cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2RGB)))
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray_frame, (7, 7), 0)
        self.processing_images.append(("Blurred", cv2.cvtColor(blurred, cv2.COLOR_GRAY2RGB)))
        
        # Apply thresholding
        _, thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY_INV)
        self.processing_images.append(("Thresholded", cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)))
        
        # Find contours
        contours_img = original_frame.copy()
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(contours_img, contours, -1, (0, 255, 0), 2)
        self.processing_images.append(("Contours", contours_img))
        
        # Process with MediaPipe hands
        results = self.hands.process(rgb_frame)
        
        # Draw hand landmarks
        annotated_frame = original_frame.copy()
        user_gesture = None
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    annotated_frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )
                
                # Detect gesture if in the right state
                if self.state == "playing":
                    user_gesture = self.detect_gesture(hand_landmarks)
        
        self.processing_images.append(("Hand Detection", annotated_frame))
        
        # Display processing steps
        self.display_processing_steps()
        
        return annotated_frame, user_gesture
    
    def display_processing_steps(self):
        # Clear canvas
        self.processing_canvas.delete("all")
        self.processing_photo_refs = []
        
        # Calculate image size and positioning
        canvas_width = self.processing_canvas.winfo_width()
        if canvas_width < 10:  # Not fully initialized yet
            canvas_width = 400
        
        num_images = len(self.processing_images)
        img_width = canvas_width // min(num_images, 3)
        img_height = img_width * 3 // 4  # 4:3 aspect ratio
        
        # Place images in grid
        for i, (label, img) in enumerate(self.processing_images):
            row = i // 3
            col = i % 3
            
            # Resize image for display
            img_resized = cv2.resize(img, (img_width, img_height))
            img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
            
            # Convert to PhotoImage
            img_pil = Image.fromarray(img_rgb)
            img_tk = ImageTk.PhotoImage(img_pil)
            self.processing_photo_refs.append(img_tk)  # Keep a reference
            
            # Add to canvas
            x = col * img_width
            y = row * (img_height + 20)  # Add space for label
            self.processing_canvas.create_image(x, y, anchor="nw", image=img_tk)
            self.processing_canvas.create_text(x + img_width//2, y + img_height + 10, text=label)
            
            # Save processing images at key moments
            if self.state == "result":
                cv2.imwrite(f"{self.output_dir}/{label.replace(' ', '_')}.jpg", img)
    
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
            
            # Convert to RGB for tkinter
            rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PhotoImage and display
            img = Image.fromarray(rgb_frame)
            img = ImageTk.PhotoImage(img)
            self.camera_label.config(image=img)
            self.camera_label.image = img
        
        # Schedule the next update
        self.root.after(10, self.update)
    
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
    
    def display_result_overlay(self, frame):
        # Display user's gesture
        cv2.putText(frame, f"You: {self.user_gesture.capitalize()}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Display computer's gesture
        cv2.putText(frame, f"Computer: {self.computer_gesture.capitalize()}", (10, 70), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Display result
        cv2.putText(frame, self.result, (frame.shape[1]//2 - 100, frame.shape[0]//2), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3)
    
    def run(self):
        self.update()
        self.root.mainloop()
    
    def cleanup(self):
        self.cap.release()
        self.hands.close()



if __name__ == "__main__":
    game = RPSGame()
    try:
        game.run()
    finally:
        game.cleanup()

