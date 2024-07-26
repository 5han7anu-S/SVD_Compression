import numpy as np
import matplotlib.pyplot as plt
from skimage import io
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


def calculate_compression_percentage(U, S, Vt, k, original_size):
    """
    Calculate the compression percentage of the image.

    Parameters:
    - U, S, Vt: SVD components of the original image
    - k: Number of singular values to retain for each channel
    - original_size: Size of the original image

    Returns:
    - compression_percentage: Percentage of the original size
    """
    compressed_size = sum([U[i][:, :k].size + S[i][:k].size + Vt[i][:k, :].size for i in range(3)])
    return (compressed_size / original_size) * 100


if __name__ == "__main__":
    image_path = 'cat.png'
    image = io.imread(image_path)

    # Perform SVD on each channel
    U = []
    S = []
    Vt = []
    for i in range(3):
        u, s, vt = svd(image[:, :, i], full_matrices=False)
        U.append(u)
        S.append(s)
        Vt.append(vt)

    k_values = np.linspace(1, 30, 7, dtype=int)
    original_size = np.prod(image.shape)

    # Reconstruct with different k
    compressed_images = [reconstruct_image(U, S, Vt, k) for k in k_values]
    compression_percentages = [calculate_compression_percentage(U, S, Vt, k, original_size) for k in k_values]

    print (compression_percentages)

    # Plot the original and compressed images
    fig, axes = plt.subplots(2, 4, figsize=(20, 10))

    for i, (ax, k, comp_img, perc) in enumerate(zip(axes.flat[:-1], k_values, compressed_images, compression_percentages)):
        ax.imshow(comp_img.astype(np.uint8))
        ax.set_title(f'Reconstruction with k={k}')
        ax.axis('off')

    axes[1, 3].imshow(image)
    axes[1, 3].set_title('Original Image')
    axes[1, 3].axis('off')

    plt.tight_layout()
    plt.savefig("results.png")
    plt.show()