import time
import replicate

def perform_face_swap(source_image_url, target_image_url):
    request_id = str(int(time.time()))

    input_data = {
        "request_id": request_id,
        "swap_image": target_image_url,
        "target_image": source_image_url
    }

    output = replicate.run(
        "yan-ops/face_swap:03d7416f38c2fa723b28fd3733d73ad8a566bf4155d273f4fe76af1d973b55db",
        input=input_data
    )

    # Check if output is a list and not empty
    if isinstance(output, list) and len(output) > 0:
        output_data = output[0]
    else:
        output_data = None

    # Retrieve the face-swapped image URL
    face_swapped_image_url = None
    if isinstance(output_data, str):
        face_swapped_image_url = output_data

    return face_swapped_image_url
