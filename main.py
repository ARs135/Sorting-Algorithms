import pygame
import random
import time
import numpy as np

# --- Constants ---
WIDTH, HEIGHT = 800, 600
BAR_COLOR = (0, 255, 0)
BG_COLOR = (0, 0, 0)
FPS = 60
list_size = 100

# --- Pygame Init ---
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sorting Visualization")
clock = pygame.time.Clock()

# --- Play Tone ---
last_sound = None

def play_tone(value, max_val, duration=0.05):
    global last_sound
    freq = 200 + (value / max_val) * 1800
    sample_rate = 44100
    n_samples = int(sample_rate * duration)

    t = np.linspace(0, duration, n_samples, False)
    waveform = 0.5 * np.sin(2 * np.pi * freq * t)

    waveform = np.int16(waveform * 32767)
    stereo_wave = np.column_stack((waveform, waveform))
    
    last_sound = pygame.sndarray.make_sound(stereo_wave)
    last_sound.play()

# --- Event Handling ---
def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

# --- Visualization Function ---
def visualize(data, highlighted_indices=[]):
    screen.fill(BG_COLOR)

    n = len(data)
    bar_width = WIDTH / n
    max_val = max(data)

    for i, val in enumerate(data):
        x = i * bar_width
        bar_height = (val / max_val) * (HEIGHT - 20)
        y = HEIGHT - bar_height

        color = (255, 0, 0) if i in highlighted_indices else BAR_COLOR
        pygame.draw.rect(screen, color, (x, y, bar_width, bar_height))

    pygame.display.flip()

    # Play tone (non-blocking)
    if highlighted_indices:
        index = highlighted_indices[0]
        play_tone(data[index], max_val)

    # Let the event loop breathe
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    time.sleep(0.01)  # very short pause between frames

# --- Quit Helper ---
def wait_for_exit():
    running = True
    while running:
        handle_events()
        clock.tick(FPS)
    pygame.quit()

# --- Generate list ---
def generate_list(size):
    data_list = []
    for i in range(1, size+1):
        data_list.append(i)
    
    return data_list

# --- Sorting Algs ---
# === Bogo Sort ===
def bogosort(data):
    sorted_data = sorted(data)
    while data != sorted_data:
        random.shuffle(data)
        # Highlight the first two bars (or any two random indices) to get sound
        visualize(data, highlighted_indices=[0, 1])

# === Bubble Sort ===
def bubblesort(data):
    size = len(data)
    for i in range(0, size):
        for j in range(0, size - i - 1):
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]

            visualize(data, [j, j + 1])

# === Insertion Sort ===
def insertionsort(data):
    size = len(data)
    for i in range(1, size):
        key = data[i]
        j = i - 1
        while j >= 0 and data[j] > key:
            data[j + 1] = data[j]
            j = j - 1
            visualize(data, [j + 1, j + 2])
        data[j + 1] = key
        visualize(data, [j + 1])

# === Selection Sort ===
def selectionsort(data):
    size = len(data)
    for i in range(size):
        min_index = i
        for j in range(i + 1, size):
            if data[j] < data[min_index]:
                min_index = j
            visualize(data, [i, j, min_index])
        data[i], data[min_index] = data[min_index], data[i]
        visualize(data, [i, min_index])

# === Merge Sort ===
def mergesort(data, left=0, right=None):
    if right is None:
        right = len(data) - 1

    if left >= right:
        return

    mid = (left + right) // 2

    mergesort(data, left, mid)
    mergesort(data, mid + 1, right)
    merge(data, left, mid, right)

def merge(data, left, mid, right):
    left_part = data[left:mid+1]
    right_part = data[mid+1:right+1]

    i = j = 0
    k = left

    while i < len(left_part) and j < len(right_part):
        if left_part[i] <= right_part[j]:
            data[k] = left_part[i]
            i += 1
        else:
            data[k] = right_part[j]
            j += 1
        visualize(data, [k])  # Highlight the merged element
        k += 1

    while i < len(left_part):
        data[k] = left_part[i]
        i += 1
        k += 1
        visualize(data, [k-1])

    while j < len(right_part):
        data[k] = right_part[j]
        j += 1
        k += 1
        visualize(data, [k-1])

# === Quick Sort ===
def quicksort(data, low=0, high=None):
    if high is None:
        high = len(data) - 1

    if low < high:
        pivot_index = partition(data, low, high)
        quicksort(data, low, pivot_index - 1)
        quicksort(data, pivot_index + 1, high)

def partition(data, low, high):
    pivot = data[high]
    i = low - 1
    for j in range(low, high):
        if data[j] < pivot:
            i += 1
            data[i], data[j] = data[j], data[i]
        visualize(data, [i, j, high])  # highlight i, j, and pivot
    data[i + 1], data[high] = data[high], data[i + 1]
    visualize(data, [i + 1, high])  # highlight swap with pivot
    return i + 1

# === Tim Sort ===
def timsort(data):
    RUN = 32
    n = len(data)

    # Step 1: Sort small runs with insertion sort
    for start in range(0, n, RUN):
        end = min(start + RUN - 1, n - 1)
        insertion_sort_range(data, start, end)

    # Step 2: Merge runs
    size = RUN
    while size < n:
        for left in range(0, n, 2 * size):
            mid = min(left + size - 1, n - 1)
            right = min(left + 2 * size - 1, n - 1)

            if mid < right:
                merge_range(data, left, mid, right)
        size *= 2

# Insertion sort over a sub-range
def insertion_sort_range(data, left, right):
    for i in range(left + 1, right + 1):
        key = data[i]
        j = i - 1
        while j >= left and data[j] > key:
            data[j + 1] = data[j]
            j -= 1
            visualize(data, [j + 1, j + 2])
        data[j + 1] = key
        visualize(data, [j + 1])

# Merge sort merge step over a sub-range
def merge_range(data, left, mid, right):
    left_part = data[left:mid + 1]
    right_part = data[mid + 1:right + 1]

    i = j = 0
    k = left

    while i < len(left_part) and j < len(right_part):
        if left_part[i] <= right_part[j]:
            data[k] = left_part[i]
            i += 1
        else:
            data[k] = right_part[j]
            j += 1
        visualize(data, [k])
        k += 1

    while i < len(left_part):
        data[k] = left_part[i]
        i += 1
        visualize(data, [k])
        k += 1

    while j < len(right_part):
        data[k] = right_part[j]
        j += 1
        visualize(data, [k])
        k += 1

# --- Running ---
if __name__ == "__main__":
    data_list = generate_list(list_size)
    random.shuffle(data_list)

    # Choose sorting algorithm here:
    # bogosort(data_list)
    # bubblesort(data_list)
    # insertionsort(data_list)
    # selectionsort(data_list)
    mergesort(data_list)
    # quicksort(data_list)
    # timsort(data_list)

    wait_for_exit()

# --- Time Complexities ---
"""
Bogo: O((n+1)!)
Bubble: O(n^2)
Insertion: O(n^2)
Selection: O(n^2)
Merge: O(n log n)
Quick: O(n log n)
Tim: O(n log n)
"""
