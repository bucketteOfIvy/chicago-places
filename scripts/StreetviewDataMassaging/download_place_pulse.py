### Author: Ashlynn Wimer
### Date: 5/19/2024
### About: This script retrieves the place-pulse-2.0.zip file currently stored
###        in a UChicago Box.

import requests
import sys

if __name__ == "__main__":
    DOWNLOAD_LINK = "https://dl.boxcloud.com/d/1/b1!lLaN28SdCHU3Y-diNGy2ZYYnzVotPXMiotHrNtl60Fmr03ems7EJYvdP07uJ1jU48QAqvJM2lL9AXPAB8ZYvSEnuL_ZxaDlTlKmaNcmb6cD0JIjqOM0wV02MLdCzVZONFE_Jy8H7jPiOHGaNvyUSd2Yu8FPi0L67d6pC0xZGLF3aD0PPSX-EqzjULvjeyGIapXHMdhEEJ27B1nwtsEMUHFpEFWpaFKXnK09A717vbU3uzABzVOy-Ilq6mRWDEwP_cvsruZ9iPsvqm83veR4Tv21ZQlbho1GIrLwod-Zg5rtrbbQ4ZDWzuQMKYWAHNjHDNmqRkGGmcE8vkIhWZz0KQQ2xoL9_FrMV9pZoBpwgyfX1OlB_oaoA1MTEO6qTLuS_amjXIUlF6yUUAo2FioZGpjAYgLXSMHjAze7P-FoolxjgbmZwaoy7ow5HQT0Yw8xCQQk2mAEXIUQVEhO8X0XvyuH3alDH--SNaKlIQBC7ucSgDCQQFKqAdM7y9Bw8j4wV8ZurixsiBfdacn4l25ais3nhbK75os722TfBBXUWLJtqTOP3kbR5pu7o3KpE55n-4KvHI93O9pXrB7m353QMWRvaukmL4Npe0dgTGpb93JYpHUW13WMs_q1fRtsJpSb0z7C6Qigxw9q3U0fNrJ2YZWnAhFKPVnBIb6yX4Pwb3MvDFIFQrUkFjbbw0GxawQFXQs7x1_4b_B8W3mw-T1xxBcftyYg9ACmz_1S-IAPFpOYS75H-L5quxwwQOAFOuPeLLnKcmqgF5v3vGdOwfOTPkAd7R4Ga1FkZ2BldKujjzaPTKknJhhsW3zU-Emd2dBWJoqTGA7nMsPa9ddD1IZNCIwMQ-W2U77a-DAFq72LCvMCkXZhKV6ChD2XQUnewOU_9xqMC5okWCCu9zyqXs8BG6R8HcnzftMCQPUhy5a1cX_q7b6SCsBJ2wUIUAvSL4icsP_rlu52fPDYLuP78r0GW49Jm8sv6rkTqKHyCSDwdZpA-bms60leAs9i2e_99zvo-kfTqS2HiT9_eFzv-KMHzLSeOiS-jqX4O7_VhWR5ttGTJiibFigaXp2_2VSQ-lnFZUBMYGQ4-FXeBeWnkf5ir16DAlZgXjbKTg-1Lj4_mXUsmi5M4fvQ1i0PXowelw7N7EVdk9tj-QprezZV9FDo7Kf2jla_G-oF2wD5u6VY9pL6w2VYdJpO1fCVas6rUvF57b_e-2WMDIAxXg8l6KfEZOKRGAgPb6TbCSD-7S8wq2Vwd_3FY7FIyBCnH_VNUa8uWKQfVCIeXJ1_qXFrleRGAzAifeMPEd56nynvfPRxCvoO-h85O5ZOUHD0DHJQD9eQLRXdrDJd_5gkEYr3teAcDWwB6IWNABgYxoqSgsj6xkzRhlC_AmTk7aoU./download"
    with requests.get(DOWNLOAD_LINK, stream=True) as r:
        r.raise_for_status()
        with open('../../data/place-pulse-2.0.zip', 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)
