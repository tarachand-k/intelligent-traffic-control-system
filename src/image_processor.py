import os
import cv2


class ImageProcessing:
    def __init__(self, input_folder, output_folder):
        self.input_folder = None
        self.output_folder = None
        self.set_input_folder(input_folder)
        self.set_output_folder(output_folder)

    def set_input_folder(self, folder_path):
        if os.path.isdir(folder_path):
            self.input_folder = folder_path
            print("Input folder set successfully.")
        else:
            print("Invalid input folder path.")

    def set_output_folder(self, folder_path):
        if os.path.isdir(folder_path):
            self.output_folder = folder_path
            print("Output folder set successfully.")
        else:
            print("Invalid output folder path.")

    def load_image(self, file_name):
        if not self.input_folder or not file_name:
            print("Input folder or image file name is invalid.")
            return None

        image_path = os.path.join(self.input_folder, str(file_name))
        if not os.path.isfile(image_path):
            print("Image does not exist.")
            return None

        return cv2.imread(image_path)

    def save_processed_img(self, lane, image):
        if not self.output_folder or not bool(image.any()):
            print("Output folder or image is empty.")
            return None

        img_path = os.path.join(self.output_folder, f"lane_{lane}.png")
        cv2.imwrite(img_path, image)
        print("Saved processed image to: " + img_path)


# Example usage
if __name__ == "__main__":
    img_processor = ImageProcessing("../input", "../output")
    img = img_processor.load_image("test.png")
    img_processor.save_processed_img(2, img)
