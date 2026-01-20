"""
Quick test script to find working IP Webcam endpoint
"""

import cv2

BASE_URL = "http://192.168.1.135:8080"

# Common IP Webcam endpoints
endpoints = [
    "/video",                    # MJPEG stream
    "/videofeed",                # Alternative MJPEG
    "/video?action=stream",      # Action parameter
    "/mjpegfeed?640x480",       # Specific resolution
    "/shot.jpg",                # Single frame
]

print(f"🔍 Testing endpoints for: {BASE_URL}\n")
print("=" * 60)

working_urls = []

for endpoint in endpoints:
    url = BASE_URL + endpoint
    print(f"\n📹 Testing: {url}")
    
    try:
        cap = cv2.VideoCapture(url)
        
        if cap.isOpened():
            print("  ✓ Stream opened successfully")
            
            # Try to read a frame
            ret, frame = cap.read()
            
            if ret and frame is not None:
                h, w = frame.shape[:2]
                print(f"  ✓ Frame read successfully ({w}x{h})")
                print(f"  ✅ THIS ENDPOINT WORKS!")
                working_urls.append(url)
            else:
                print("  ✗ Could not read frame")
            
            cap.release()
        else:
            print("  ✗ Could not open stream")
            
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\n" + "=" * 60)
print("\n📊 RESULTS:\n")

if working_urls:
    print("✅ Working URLs found:")
    for url in working_urls:
        print(f"   • {url}")
    
    print(f"\n💡 Use this URL in Camera Setup:")
    print(f"   {working_urls[0]}")
else:
    print("❌ No working endpoints found!")
    print("\n🔧 Troubleshooting:")
    print("   1. Check if IP Webcam app is running")
    print("   2. Verify the IP address is correct")
    print("   3. Make sure PC and phone are on same WiFi")
    print("   4. Try opening in browser: " + BASE_URL)

print("\n" + "=" * 60)
