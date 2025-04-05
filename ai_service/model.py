from google import genai
import json
import time
import os


class GeminiModel:
    def __init__(self, api_key=None):
        self.api_key = (
            api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("API_KEY")
        )
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-1.5-flash-002"

        # Định nghĩa các prompts theo loại movement
        self.movement_prompts = {
            "cpr": """
            Đây là video thực hiện động tác {movement_name}, đưa ra tổng điểm ?/100.
            Phân tích Chain of Thought (Yêu cầu thực hiện trước khi xuất JSON):
            Hãy trình bày quá trình suy luận của bạn theo từng bước, tương ứng với các tiêu chí đánh giá dưới đây. Với mỗi tiêu chí:
            1.  Mô tả ngắn gọn hành động quan sát được trong video liên quan đến tiêu chí đó.
            2.  So sánh hành động đó với tiêu chuẩn CPR lý tưởng.
            3.  Giải thích ngắn gọn lý do cho điểm (hoặc không cho điểm/trừ điểm) cho tiêu chí đó.
                *Ví dụ cho một bước:* "CoT 2a - Vị trí đặt tay: Quan sát thấy người thực hiện đặt hai bàn tay chồng lên nhau ở giữa ngực nạn nhân. Vị trí này có vẻ hơi cao so với nửa dưới xương ức theo khuyến nghị. Do đó, tiêu chí này chưa hoàn toàn tối ưu."

            **Tiêu chí đánh giá chi tiết (Dùng cho phân tích CoT):**

            *   **1. Đánh giá ban đầu & Chuẩn bị (Tổng phụ: 10 điểm)**
                *   (CoT 1a) Kiểm tra đáp ứng (lay gọi): (0-5 điểm)
                *   (CoT 1b) Kiểm tra mạch cảnh & nhịp thở (trong 5-10 giây): (0-5 điểm)
            *   **2. Ép tim ngoài lồng ngực (Tổng phụ: 55 điểm)**
                *   (CoT 2a) Vị trí đặt tay (nửa dưới xương ức): (0-10 điểm)
                *   (CoT 2b) Tư thế người cấp cứu (vai thẳng trên tay, khuỷu tay thẳng): (0-5 điểm)
                *   (CoT 2c) Tần số ép tim (mục tiêu 100-120 lần/phút): (0-15 điểm)
                *   (CoT 2d) Độ sâu ép tim (mục tiêu 5-6 cm): (0-20 điểm)
                *   (CoT 2e) Để ngực nảy lên hoàn toàn (Chest Recoil): (0-5 điểm)
            *   **3. Thông khí/Thổi ngạt (Tổng phụ: 20 điểm)**
                *   (CoT 3a) Khai thông đường thở (ngửa đầu - nâng cằm): (0-5 điểm)
                *   (CoT 3b) Kỹ thuật thổi ngạt (kín, bịt mũi, thời gian hợp lý): (0-5 điểm)
                *   (CoT 3c) Hiệu quả thổi ngạt (lồng ngực nhô lên): (0-10 điểm)
            *   **4. Chu kỳ & Tính liên tục (Tổng phụ: 15 điểm)**
                *   (CoT 4a) Tỷ lệ ép tim/thổi ngạt (30:2): (0-10 điểm)
                *   (CoT 4b) Giảm thiểu gián đoạn (<10 giây): (0-5 điểm)

            **Output cuối cùng (Định dạng JSON có cấu trúc):**
            Sau khi hoàn thành phân tích Chain of Thought ở trên, hãy cung cấp kết quả tổng hợp **CHỈ** dưới dạng JSON như sau.
            *   `total_point`: Tổng điểm từ 0-100 dựa trên phân tích CoT.
            *   `detailed_summary`: Một đối tượng JSON chứa các nhận xét chi tiết, bao gồm:
                *   `score_breakdown`: Một đối tượng chứa điểm số (dưới dạng chuỗi "Điểm/Tổng") cho từng nhóm tiêu chí chính.
                *   `strengths`: Một mảng (array) các chuỗi (string), mỗi chuỗi mô tả một điểm mạnh chính dựa trên phân tích CoT.
                *   `areas_for_improvement`: Một mảng (array) các chuỗi (string), mỗi chuỗi mô tả một điểm yếu/cần cải thiện chính dựa trên phân tích CoT.
            """,
            "heimlich": """
            Đây là video thực hiện động tác {movement_name}, đưa ra tổng điểm ?/100.
            Phân tích Chain of Thought (Yêu cầu thực hiện trước khi xuất JSON):
            Hãy trình bày quá trình suy luận của bạn theo từng bước, tương ứng với các tiêu chí đánh giá dưới đây. Với mỗi tiêu chí:
            1.  Mô tả ngắn gọn hành động quan sát được trong video liên quan đến tiêu chí đó.
            2.  So sánh hành động đó với tiêu chuẩn Heimlich lý tưởng.
            3.  Giải thích ngắn gọn lý do cho điểm (hoặc không cho điểm/trừ điểm) cho tiêu chí đó.
                *Ví dụ cho một bước:* "CoT 3b - Vị trí đặt tay: Quan sát thấy người thực hiện đặt nắm đấm ngay dưới xương sườn của nạn nhân. Vị trí này hơi cao so với hướng dẫn là 'trên rốn, dưới mũi ức'. Do đó, tiêu chí này chưa hoàn toàn chính xác theo video tham chiếu, trừ 5 điểm."
            **Tiêu chí đánh giá chi tiết (Dùng cho phân tích CoT):**

            *   **1. Nhận Biết Tình Huống (Tổng phụ: 20 điểm)**
                *   (CoT 1a) Có biểu hiện nhận biết/phân biệt được mức độ tắc nghẽn (một phần/hoàn toàn) không?: (0-10 điểm)
                *   (CoT 1b) Có biểu hiện nhận biết được các dấu hiệu tắc nghẽn (ôm cổ, khó thở...) không?: (0-10 điểm)
            *   **2. Xử Lý Tắc Nghẽn Một Phần (Nếu tình huống là tắc nghẽn một phần) (Tổng phụ: 20 điểm)**
                *   (CoT 2a) Có khuyến khích ho mạnh & hướng dẫn cúi người không?: (0-10 điểm)
                *   (CoT 2b) Có thực hiện vỗ lưng đúng vị trí (giữa 2 bả vai) như video tham chiếu không?: (0-10 điểm)
            *   **3. Kỹ Thuật Heimlich (Nếu tình huống là tắc nghẽn hoàn toàn) (Tổng phụ: 60 điểm)**
                *   (CoT 3a) Tư thế người sơ cứu (đứng sau, vững chắc) có đúng không?: (0-10 điểm)
                *   (CoT 3b) Vị trí đặt tay (nắm đấm trên rốn, dưới mũi ức) có chính xác không?: (0-25 điểm)
                *   (CoT 3c) Kỹ thuật đẩy bụng (vào trong & lên trên, mạnh, dứt khoát, lặp lại) có đúng không?: (0-25 điểm)

            **Output cuối cùng (Định dạng JSON có cấu trúc):**
            Sau khi hoàn thành phân tích Chain of Thought ở trên, hãy cung cấp kết quả tổng hợp **CHỈ** dưới dạng JSON như sau.
            *   `total_point`: Tổng điểm từ 0-100 dựa trên phân tích CoT.
            *   `detailed_summary`: Một đối tượng JSON chứa các nhận xét chi tiết, bao gồm:
                *   `score_breakdown`: Một đối tượng chứa điểm số (dưới dạng chuỗi "Điểm/Tổng") cho từng nhóm tiêu chí chính **đã được đánh giá** (Không bao gồm tiêu chí Gọi Hỗ Trợ). Ví dụ: "nhan_biet_tinh_huong": "18/20".
                *   `strengths`: Một mảng (array) các chuỗi (string), mỗi chuỗi mô tả một điểm mạnh chính quan sát được, so với video tham chiếu.
                *   `areas_for_improvement`: Một mảng (array) các chuỗi (string), mỗi chuỗi mô tả một điểm yếu/cần cải thiện chính quan sát được, so với video tham chiếu.
            """,
            "recovery": """
            Đây là video thực hiện động tác {movement_name}, đưa ra tổng điểm ?/100.

            Phân tích Chain of Thought (Yêu cầu thực hiện trước khi xuất JSON):
            Hãy trình bày quá trình suy luận của bạn theo từng bước, tương ứng với các tiêu chí đánh giá dưới đây. Với mỗi tiêu chí:
            1.  Mô tả ngắn gọn hành động quan sát được trong video liên quan đến tiêu chí đó.
            2.  So sánh hành động đó với tiêu chuẩn thực hiện "Tư thế hồi sức" lý tưởng.
            3.  Giải thích ngắn gọn lý do cho điểm (hoặc không cho điểm/trừ điểm) cho tiêu chí đó.
                *Ví dụ cho một bước:* "CoT 2a - Đặt tay gần vuông góc: Quan sát thấy người thực hiện nâng tay gần của nạn nhân lên, khuỷu tay gập, tạo thành một góc khoảng 80 độ so với thân mình. Tiêu chuẩn là khoảng 90 độ. Do gần đạt chuẩn và thao tác đúng nên cho điểm cao, nhưng có thể trừ nhẹ vì chưa hoàn toàn vuông góc."

            **Tiêu chí đánh giá chi tiết (Dùng cho phân tích CoT - ĐÃ ĐIỀU CHỈNH CHO TƯ THẾ HỒI SỨC):**

            *   **1. Chuẩn bị & Thiết lập ban đầu (Tổng phụ: 10 điểm)**
                *   (CoT 1a) Tiếp cận và Quỳ đúng vị trí (bên cạnh nạn nhân): (0-5 điểm)
                *   (CoT 1b) Thao tác ban đầu mạch lạc, không lúng túng: (0-5 điểm)
            *   **2. Định vị Tay & Chân Nạn nhân (Tổng phụ: 45 điểm)**
                *   (CoT 2a) Đặt tay gần vuông góc (đúng góc 90 độ, lòng bàn tay ngửa): (0-15 điểm)
                *   (CoT 2b) Đặt tay xa áp má (mu bàn tay áp má đối diện, giữ tay): (0-15 điểm)
                *   (CoT 2c) Co chân xa (gối co lên, bàn chân đặt phẳng sàn): (0-15 điểm)
            *   **3. Thao tác Lăn & Điều chỉnh tư thế (Tổng phụ: 35 điểm)**
                *   (CoT 3a) Kỹ thuật lăn (dùng gối kéo, nhẹ nhàng, có kiểm soát): (0-15 điểm)
                *   (CoT 3b) Điều chỉnh Ngửa đầu - Nâng cằm (QUAN TRỌNG NHẤT - đảm bảo đường thở): (0-15 điểm)
                *   (CoT 3c) Ổn định tư thế cuối (nằm nghiêng, chân trên gập 90 độ): (0-5 điểm)
            *   **4. Tính Tuần tự & An toàn chung (Tổng phụ: 10 điểm)**
                *   (CoT 4a) Thực hiện đúng trình tự các bước: (0-5 điểm)
                *   (CoT 4b) Thao tác chung nhẹ nhàng, an toàn cho nạn nhân: (0-5 điểm)

            **Output cuối cùng (Định dạng JSON có cấu trúc):**
            Sau khi hoàn thành phân tích Chain of Thought ở trên, hãy cung cấp kết quả tổng hợp **CHỈ** dưới dạng JSON như sau.
            *   `total_point`: Tổng điểm từ 0-100 dựa trên phân tích CoT.
            *   `detailed_summary`: Một đối tượng JSON chứa các nhận xét chi tiết, bao gồm:
                *   `score_breakdown`: Một đối tượng chứa điểm số (dưới dạng chuỗi "Điểm/Tổng") cho từng nhóm tiêu chí chính (ví dụ: "initial_setup", "limb_positioning", "rolling_adjustment", "overall_quality").
                *   `strengths`: Một mảng (array) các chuỗi (string), mỗi chuỗi mô tả một điểm mạnh chính dựa trên phân tích CoT.
                *   `areas_for_improvement`: Một mảng (array) các chuỗi (string), mỗi chuỗi mô tả một điểm yếu/cần cải thiện chính dựa trên phân tích CoT.
            """,
            "nosebleed": """
            Đây là video thực hiện động tác {movement_name}, đưa ra tổng điểm ?/100.

            Phân tích Chain of Thought (Yêu cầu thực hiện trước khi xuất JSON):
            Hãy trình bày quá trình suy luận của bạn theo từng bước, tương ứng với các tiêu chí đánh giá dưới đây. Với mỗi tiêu chí:
            1.  Mô tả ngắn gọn hành động quan sát được trong video liên quan đến tiêu chí đó.
            2.  So sánh hành động đó với tiêu chuẩn sơ cứu chảy máu cam lý tưởng.
            3.  Giải thích ngắn gọn lý do cho điểm (hoặc không cho điểm/trừ điểm) cho tiêu chí đó.
            Ví dụ cho một bước: "CoT 2a - Vị trí ép: Quan sát thấy người thực hiện dùng hai ngón tay bóp vào phần cánh mũi mềm của nạn nhân. Vị trí này chính xác theo khuyến nghị sơ cứu. Do đó, tiêu chí này đạt điểm tối đa."

            **Tiêu chí đánh giá chi tiết (Dùng cho phân tích CoT):**

            *   **1. Tư thế nạn nhân (Tổng phụ: 35 điểm)**
                *   (CoT 1a) Tư thế ngồi: Hướng dẫn/để nạn nhân ngồi thẳng, không nằm. (0-10 điểm)
                *   (CoT 1b) Nghiêng người về phía trước: Hướng dẫn/để nạn nhân nghiêng/cúi đầu và thân người về phía trước (tránh ngửa ra sau). (0-25 điểm)
            *   **2. Kỹ thuật cầm máu (Tổng phụ: 50 điểm)**
                *   (CoT 2a) Vị trí ép: Dùng ngón tay (thường là ngón cái và ngón trỏ) bóp chặt vào phần **cánh mũi mềm** (phần chóp mũi, dưới xương sống mũi), không phải phần xương cứng. (0-25 điểm)
                *   (CoT 2b) Lực ép và duy trì: Bóp đủ mạnh và **giữ liên tục**, không thả ra kiểm tra thường xuyên. (0-15 điểm)
                *   (CoT 2c) Hướng dẫn thở: Khuyên nạn nhân thở bằng miệng trong khi mũi đang bị bóp. (0-10 điểm)
            *   **3. Duy trì và Theo dõi (Tổng phụ: 15 điểm)**
                *   (CoT 3a) Duy trì tư thế ép: Giữ vững thao tác bóp mũi và tư thế nghiêng người về phía trước một cách ổn định trong suốt thời gian thực hiện được quay trong video. (0-15 điểm)
            *   **(Implicit) 4. Tránh các hành động sai (Được đánh giá lồng ghép trong các tiêu chí trên)**
                *   *(Không ngửa mặt/đầu ra sau - nằm trong CoT 1b)*
                *   *(Không nằm xuống - nằm trong CoT 1a)*
                *   *(Không nhét vật lạ (bông, giấy) sâu vào mũi - không phải là hành động trực tiếp cần thực hiện, nhưng nếu video có cảnh báo thì ghi nhận)*

            **Output cuối cùng (Định dạng JSON có cấu trúc):**
            Sau khi hoàn thành phân tích Chain of Thought ở trên, hãy cung cấp kết quả tổng hợp **CHỈ** dưới dạng JSON như sau.
            *   `total_point`: Tổng điểm từ 0-100 dựa trên phân tích CoT.
            *   `detailed_summary`: Một đối tượng JSON chứa các nhận xét chi tiết, bao gồm:
                *   `score_breakdown`: Một đối tượng chứa điểm số (dưới dạng chuỗi "Điểm/Tổng") cho từng nhóm tiêu chí chính (Tư thế, Kỹ thuật, Duy trì).
                *   `strengths`: Một mảng (array) các chuỗi (string), mỗi chuỗi mô tả một điểm mạnh chính dựa trên phân tích CoT.
                *   `areas_for_improvement`: Một mảng (array) các chuỗi (string), mỗi chuỗi mô tả một điểm yếu/cần cải thiện chính dựa trên phân tích CoT.
            """,
            "shock": """
            Đây là video thực hiện động tác {movement_name}, đưa ra tổng điểm ?/100.

            Phân tích Chain of Thought (Yêu cầu thực hiện trước khi xuất JSON):
            Hãy trình bày quá trình suy luận của bạn theo từng bước, tương ứng với các tiêu chí đánh giá dưới đây. Với mỗi tiêu chí:
            1.  Mô tả ngắn gọn hành động quan sát được trong video liên quan đến tiêu chí đó.
            2.  So sánh hành động đó với tiêu chuẩn sơ cứu choáng ngất lý tưởng.
            3.  Giải thích ngắn gọn lý do cho điểm (hoặc không cho điểm/trừ điểm) cho tiêu chí đó.
            Ví dụ cho một bước: "CoT 1b - Nâng cao chân: Quan sát thấy người thực hiện đặt chân nạn nhân lên một chiếc ghế, đảm bảo chân cao hơn rõ rệt so với đầu. Hành động này đúng theo khuyến nghị để tăng lưu lượng máu lên não. Do đó, tiêu chí này đạt điểm tối đa."

            **Tiêu chí đánh giá chi tiết (Dùng cho phân tích CoT):**

            *   **1. Tư thế nạn nhân (Tổng phụ: 35 điểm)**
                *   (CoT 1a) Đặt nạn nhân nằm: Nhanh chóng đặt nạn nhân nằm ngửa trên mặt phẳng an toàn. (0-5 điểm)
                *   (CoT 1b) Nâng cao chân: Nâng hai chân của nạn nhân lên cao hơn đầu một cách rõ rệt (ví dụ: kê lên ghế, vật dụng hoặc người khác giữ). (0-30 điểm)
            *   **2. Hành động hỗ trợ ban đầu (Tổng phụ: 50 điểm)**
                *   (CoT 2a) Nới lỏng quần áo: Kiểm tra và chủ động nới lỏng quần áo bó sát (cổ áo, thắt lưng...). (0-15 điểm)
                *   (CoT 2b) Đảm bảo đường thở (Xoay đầu): Đặt đầu nạn nhân nghiêng sang một bên để tránh tụt lưỡi hoặc hít sặc. (0-25 điểm)
                *   (CoT 2c) Đánh giá & Giữ ấm (Nếu cần): Đánh giá sơ bộ thân nhiệt và đắp chăn/áo mỏng nếu nạn nhân có vẻ lạnh. (0-10 điểm)
            *   **3. Theo dõi và Kích thích(Tổng phụ: 15 điểm)**
                *   (CoT 3a) Mô phỏng Theo dõi & Kích thích hồi tỉnh: Thực hiện các hành động mô phỏng việc theo dõi (nhìn vào mặt, ngực nạn nhân) VÀ kích thích nhẹ nhàng (gọi tên giả định, vỗ nhẹ má, dùng tay mô phỏng lau mặt...). (0-15 điểm)
            *   **(Implicit) 4. Tránh các hành động sai (Được đánh giá lồng ghép trong các tiêu chí trên)**
                *   *(Không đỡ nạn nhân ngồi dậy quá sớm)*
                *   *(Không cho ăn/uống khi nạn nhân chưa hoàn toàn tỉnh táo)*
                *   *(Không tụ tập quá đông xung quanh - nằm trong CoT 3a)*

            **Output cuối cùng (Định dạng JSON có cấu trúc):**
            Sau khi hoàn thành phân tích Chain of Thought ở trên, hãy cung cấp kết quả tổng hợp **CHỈ** dưới dạng JSON như sau.
            *   `total_point`: Tổng điểm từ 0-100 dựa trên phân tích CoT.
            *   `detailed_summary`: Một đối tượng JSON chứa các nhận xét chi tiết, bao gồm:
                *   `score_breakdown`: Một đối tượng chứa điểm số (dưới dạng chuỗi "Điểm/Tổng") cho từng nhóm tiêu chí chính ("positioning": Tư thế, "initial_actions": Hành động hỗ trợ, "monitoring_follow_up": Theo dõi/Xử lý).
                *   `strengths`: Một mảng (array) các chuỗi (string), mỗi chuỗi mô tả một điểm mạnh chính dựa trên phân tích CoT.
                *   `areas_for_improvement`: Một mảng (array) các chuỗi (string), mỗi chuỗi mô tả một điểm yếu/cần cải thiện chính dựa trên phân tích CoT.
            """,
            # Default prompt for other movements
            "default": """
            This video is about {movement_name} movement, rate this video point out of 100, ?/100
            "Comment" on this movement. Comment is in general about the movement,
            "Detail" is rating in detailed about the good and bad part of the movement things to improve why the score is ?/100 
            IMPORTANT: Respond ONLY in JSON format like this example:
            {{
                "total_point": 85,
                "detailed_summary": {{
                    "comment": "The movement is very good overall!",
                    "strengths": ["Good form", "Proper execution"],
                    "areas_for_improvement": ["Could improve timing", "Better posture needed"]
                }}
            }}
            """,
        }

    def _get_movement_type(self, movement_name):
        """
        Identify movement type from the movement name.
        """
        movement_name = movement_name.lower()
        if "cpr" in movement_name:
            return "cpr"
        elif "heimlich" in movement_name:
            return "heimlich"
        elif "recovery" in movement_name:
            return "recovery"
        elif "nosebleed" in movement_name:
            return "nosebleed"
        elif "shock" in movement_name:
            return "shock"
        else:
            return "default"

    def predict(self, video_file, movement_name="exercise"):
        """
        Process video with Gemini API and return assessment based on movement type
        """
        try:
            # Get the prompt template based on movement type
            movement_type = self._get_movement_type(movement_name)
            prompt_template = self.movement_prompts.get(
                movement_type, self.movement_prompts["default"]
            )

            # Format the prompt with movement name
            prompt = prompt_template.format(movement_name=movement_name)

            # Check if we're using a URI path or a file
            if isinstance(video_file, str) and os.path.exists(video_file):
                # Process file upload path
                print(f"Uploading file: {video_file}")
                with open(video_file, "rb") as f:
                    uploaded_file = self.client.files.upload(
                        file=f, config={"mime_type": "video/mp4"}
                    )
            else:
                # Handle case where video_file is already a file object
                uploaded_file = self.client.files.upload(
                    file=video_file, config={"mime_type": "video/mp4"}
                )

            # Wait for processing
            gemini_file = self.client.files.get(name=uploaded_file.name)

            print("Processing video...", end="")
            while gemini_file.state.name == "PROCESSING":
                print(".", end="", flush=True)
                time.sleep(1)
                gemini_file = self.client.files.get(name=gemini_file.name)
            print(" Done!")

            if gemini_file.state.name == "FAILED":
                return {
                    "error": "Video processing failed",
                    "details": gemini_file.state.name,
                }

            # Generate content with Gemini
            model = (
                "gemini-1.5-flash-002"
                if movement_type == "default"
                else "gemini-1.5-flash-002"
            )
            response = self.client.models.generate_content(
                model=model,
                contents=[gemini_file, prompt],
            )

            # Parse the response
            json_text = response.text.strip()

            # Extract JSON from the response
            json_start_index = -1
            json_end_index = -1

            code_block_start = json_text.find("```json")
            if code_block_start != -1:
                json_start_index = code_block_start + 7
                code_block_end = json_text.find("```", json_start_index)
                if code_block_end != -1:
                    json_end_index = code_block_end
            else:
                json_start_index = json_text.find("{")
                if json_start_index != -1:
                    json_end_index = json_text.rfind("}") + 1

            if (
                json_start_index != -1
                and json_end_index != -1
                and json_start_index < json_end_index
            ):
                json_data = json.loads(
                    json_text[json_start_index:json_end_index].strip()
                )
                return json_data
            else:
                return {
                    "error": "Could not parse JSON response",
                    "raw_response": json_text,
                }

        except Exception as e:
            return {"error": str(e)}

    def save_video_uri(self, video_path, uri_file_path=None):
        """
        Upload video and save URI to a file
        """
        try:
            if uri_file_path is None:
                uri_file_path = os.path.splitext(video_path)[0] + ".txt"

            # Check if URI file exists
            if os.path.exists(uri_file_path):
                with open(uri_file_path, "r") as f:
                    video_uri = f.read().strip()
                print(f"Using existing video URI: {video_uri}")
                return self.client.files.get(name=video_uri)

            # Upload new file
            print(f"Uploading file: {video_path}")
            with open(video_path, "rb") as f:
                video_file = self.client.files.upload(file=f)

            print(f"Completed upload: {video_file.uri}")

            # Save URI to file
            with open(uri_file_path, "w") as f:
                f.write(video_file.uri)

            print(f"URI saved to {uri_file_path}")
            return video_file

        except Exception as e:
            print(f"Error saving video URI: {str(e)}")
            return None


# Initialize model
model = GeminiModel()
