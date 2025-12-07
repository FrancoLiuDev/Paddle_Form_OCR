#!/bin/bash
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║         空白線檢測比對 (相同參數: scan-step=1, threshold=199)        ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# fuji.png
echo "【圖片 1: fuji.png】"
result1=$(python3 preprocess_hough.py --input ../fuji.png --output result_with_lines.jpg --show-lines --detect-blanks --scan-step 1 --white-threshold 199 --min-blank 50 --degree 30 2>&1)
scanned1=$(echo "$result1" | grep "掃描線總數" | grep -oP '\d+(?= 條)')
detected1=$(echo "$result1" | grep "檢測到的空白線" | grep -oP '\d+(?= 條)')
filtered1=$(echo "$result1" | grep "過濾掉的線" | grep -oP '\d+(?= 條)')
angle1=$(echo "$result1" | grep -m1 "掃描角度:" | grep -oP '[\d.]+(?=°)' | tail -1)

echo "  掃描角度: ${angle1}°"
echo "  掃描線總數: ${scanned1} 條"
echo "  檢測到空白線: ${detected1} 條"
echo "  過濾掉的線: ${filtered1} 條"
echo ""

# fuji45.png
echo "【圖片 2: fuji45.png】"
result2=$(python3 preprocess_hough.py --input ../fuji45.png --output result45_with_lines.jpg --show-lines --detect-blanks --scan-step 1 --white-threshold 199 --min-blank 50 --degree 30 2>&1)
scanned2=$(echo "$result2" | grep "掃描線總數" | grep -oP '\d+(?= 條)')
detected2=$(echo "$result2" | grep "檢測到的空白線" | grep -oP '\d+(?= 條)')
filtered2=$(echo "$result2" | grep "過濾掉的線" | grep -oP '\d+(?= 條)')
angle2=$(echo "$result2" | grep -m1 "掃描角度:" | grep -oP '[\d.]+(?=°)' | tail -1)

echo "  掃描角度: ${angle2}°"
echo "  掃描線總數: ${scanned2} 條"
echo "  檢測到空白線: ${detected2} 條"
echo "  過濾掉的線: ${filtered2} 條"
echo ""

# 比較
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                           差異比較                              ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
diff_scanned=$((scanned2 - scanned1))
diff_detected=$((detected2 - detected1))
diff_filtered=$((filtered2 - filtered1))

echo "  掃描線數差異: $diff_scanned 條 (fuji45.png 多)"
echo "  檢測空白線差異: $diff_detected 條 (fuji45.png 多)"
echo "  過濾線數差異: $diff_filtered 條"
echo "  角度差異: ${angle1}° vs ${angle2}°"
