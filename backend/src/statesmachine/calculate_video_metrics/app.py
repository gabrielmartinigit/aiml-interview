import boto3
from PIL import Image
from io import BytesIO
from moviepy.editor import VideoFileClip

rekognition = boto3.client("rekognition")
NOT_ALLOWED = ["Glasses", "Hat", "Cap"]


def identify_objects(frames_list, objects_list):
    for frame in frames_list:
        # Convert frame to bytes
        frame_bytes = frame_to_bytes(frame)

        # Detect objects in the frame
        response = rekognition.detect_labels(Image={"Bytes": frame_bytes})

        # Extract the identified objects
        for label in response["Labels"]:
            if label["Name"] in NOT_ALLOWED:
                if label["Name"] not in objects_list:
                    objects_list.append(label["Name"])

    return objects_list


def frame_to_bytes(frame):
    # Convert NumPy array to PIL Image
    pil_image = Image.fromarray(frame)

    # Convert PIL Image to bytes
    image_stream = BytesIO()
    pil_image.save(image_stream, format="JPEG")
    image_bytes = image_stream.getvalue()
    image_stream.close()
    return image_bytes


def extract_frames(video_path, frames_list):
    # Load the video clip
    video_clip = VideoFileClip(video_path)

    # Get the duration of the video
    duration = video_clip.duration

    # Set the step size to 5 seconds
    step_size = 5

    # Iterate over each frame and extract frames every 5 seconds
    for t in range(0, int(duration), step_size):
        # Get frame at current time
        frame = video_clip.get_frame(t)
        frames_list.append(frame)

    # Close the video clip
    video_clip.close()

    return frames_list


if __name__ == "__main__":
    # Extract frames
    frames = extract_frames("9574a2ea-e0e0-40fd-86bf-4a37c8a4628d.qt", [])

    # Identify objects
    objects = identify_objects(frames, [])
    print(objects)

    print("Frame extraction completed.")
