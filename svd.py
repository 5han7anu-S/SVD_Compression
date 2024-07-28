import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from scipy.linalg import svd

def reconstruct_image(U, S, Vt, k):
    """
    Reconstruct an image using Singular Value Decomposition (SVD) components.

    Parameters:
    - U, S, Vt: SVD components of the original image
    - k: Number of singular values to retain for each channel

    Returns:
    - reconstructed_image: 3D numpy array (compressed color image) in uint8 format
    """
    reconstructed_image = np.zeros((U[0].shape[0], Vt[0].shape[1], 3), dtype=np.float32)
    
    for i in range(3):
        Uk = U[i][:, :k]
        Sk = np.diag(S[i][:k])
        Vtk = Vt[i][:k, :]
        reconstructed_image[:, :, i] = np.dot(Uk, np.dot(Sk, Vtk))
    
    # Clip values for valid rgb range
    reconstructed_image = np.clip(reconstructed_image, 0, 255).astype(np.uint8)
    
    return reconstructed_image


def calculate_compression_percentage(U, S, Vt, k):
    """
    Calculate the compression percentage of the image.

    Parameters:
    - U, S, Vt: SVD components of the original image
    - k: Number of singular values to retain
    - original_size: Size of the original image in bytes

    Returns:
    - compression_percentage: Compression percentage relative to the original size
    """

    compressed_size = sum([U[i][:, :k].size + S[i][:k].size + Vt[i][:k, :].size for i in range(3)])
    original_size = sum ([U[i].size + S[i].size + Vt[i].size for i in range (3)])

    return ((compressed_size / original_size)) * 100

def get_log_spaced_values(length):
    # Generate 8 log-spaced values between 1 and length
    log_spaced_values = np.logspace(0, np.log10(length), 8, dtype=int)
    
    # Ensure unique values and sort them
    log_spaced_values = np.unique(log_spaced_values)
    
    # If necessary, adjust to ensure exactly 8 unique values
    while len(log_spaced_values) < 8:
        additional_values = np.linspace(1, length, 8 - len(log_spaced_values), dtype=int)
        log_spaced_values = np.unique(np.concatenate((log_spaced_values, additional_values)))
    
    return log_spaced_values.tolist()

def load_image(image_path):
    # Load the image using Pillow and convert to RGB
    pil_image = Image.open(image_path).convert('RGB')
    return np.array(pil_image)

if __name__ == "__main__":
    image_path = 'images/cat.png'
    image = load_image(image_path)

    # Perform SVD on each channel
    U = []
    S = []
    Vt = []
    for i in range(3):
        u, s, vt = svd(image[:, :, i], full_matrices=False)
        U.append(u)
        S.append(s)
        Vt.append(vt)

    #k_values = np.linspace(0, 50, 7, dtype=int)
    k_values = get_log_spaced_values (len(S[0]))
    
    # Reconstruct with different k
    compressed_images = [reconstruct_image(U, S, Vt, k) for k in k_values]
    compression_percentages = [calculate_compression_percentage(U, S, Vt, k) for k in k_values]

    # Plot the original and compressed images
    fig, axes = plt.subplots(2, 4, figsize=(20, 10))
    plt.subplots_adjust(wspace=0.1, hspace=0.2)

    for i, (ax, k, comp_img, perc) in enumerate(zip(axes.flat[:-1], k_values, compressed_images, compression_percentages)):
        ax.imshow(comp_img.astype(np.uint8))
        ax.set_title(f'k={k}', fontsize=22, pad=10)
        ax.text(0.5, -0.1, f'{perc:.2f}% of Original Size', fontsize=18, ha='center', transform=ax.transAxes)
        ax.axis('off')

    axes[1, 3].imshow(image)
    axes[1, 3].set_title(f'Original Image (k={len(S[0])})', fontsize=22)
    axes[1, 3].text(0.5, -0.1, '100% of Original Size', fontsize=18, ha='center', transform=axes[1, 3].transAxes)
    axes[1, 3].axis('off')

    plt.tight_layout()
    plt.savefig("images/results.png")
