### Bao gồm 4 loại API chính trong app:
- Dữ liệu của user (bao gồm tên, gmail,... và auth token)
- Danh sách các videos
- Danh sách các quiz, quiz attempts và thực hiện quiz
- Lấy kết quả trả về của AI model trong AI service, thực hiện gửi request đến AI model trong AI service
### Vấn đề protect routes và đăng nhập
- Vấn đề này được xử lý bằng việc mọi API routes đều được protect bằng auth middleware, điều này có nghĩa là mỗi request được gửi tới Go backend server đều sẽ thông qua auth middleware, kiểm tra xem token có (còn) hiệu lực hay không, nếu không thì trả về httpStatusUnauthorized.
- Nhiệm vụ của phía frontend:
	- Phía frontend sẽ implement chức năng đăng nhập bằng google và lưu auth token vào app và đính kèm vào header cho mỗi request
	- Nếu có repsonse nào từ server với status code là httpStatusUnauthorized thì tiến hành chuyển hướng người dùng về giao diện đăng nhập và xoá token hiện tại
	- Lúc init load, sau khi đăng nhập thành công thì tiến hành get dữ liệu user để cập nhật UI và vào trang chính. Để biết khi nào đăng nhập thành công, gọi hàm onAuthChange của Firebase
### Dữ liệu của user
1. Lấy dữ liệu của user hiện đang đăng nhập
- Endpoint:  **GET** `/api/v1/user`
- Response thành công:
```json
{
	"email": "mythonggg@gmail.com",
	"name": "Nguyễn Thống",
	"picture": "https://lh3.googleusercontent.com/a/ACg8ocLpiohxen3uDqvuQpB19F-DwnpPT2pypLHBiKhoPSs9kjihvlIg=s96-c",
}
```
- Response thất bại:
```json
{
	"error": "Cannot find the user"
}
```
Hoặc có thể thất bại do trường hợp người dùng chưa đăng nhập với http status unauthorized, nếu nhận được response với status unauthorized, mặc định chuyển hướng người dùng về giao diện đăng nhập (xoá token nếu cần thiết)
```json
{
	"error" : "Invalid or expired token"
}
```
### Danh sách các videos
1. Lấy tất cả video
- Endpoint: **GET** `/api/v1/videos`
- Response:
```json
[

  {

    "id": "video123",

    "title": "How to Perform CPR",

    "description": "Step by step guide to perform CPR correctly",

    "videoUrl": "https://storage.url/video.mp4",

    "thumbnailUrl": "https://storage.url/thumbnail.jpg",

    "category": "cpr",

    "duration": 360,

    "created": "2023-10-15T14:30:00Z"

  },
  ...
```
2. Lấy video filtered theo thể loại
- Endpoint: **GET** `/api/v1/videos/category/:category`
```json
# same as above
```
3. Lấy video theo video id
- Endpoint: **GET** `/api/v1/videos/:id`
```json
{

  "id": "video123",

  "title": "How to Perform CPR",

  "description": "Step by step guide to perform CPR correctly",

  "videoUrl": "https://storage.url/video.mp4",

  "thumbnailUrl": "https://storage.url/thumbnail.jpg",

  "category": "cpr",

  "duration": 360,

  "created": "2023-10-15T14:30:00Z"

}
```
4. Response thất bại: `404: Video not found`

### Danh sách các quiz, quiz attempts và thực hiện quiz
1. Lấy tất cả quizzes
	- Endpoint: **GET** `/api/v1/quizzes`
```json
[

  {

    "id": "quiz123",

    "title": "CPR Knowledge Test",

    "description": "Test your knowledge of CPR techniques",

    "category": "cpr",

    "difficulty": "beginner",

    "timeLimit": 600,

    "questionCount": 10

  },

  ...

]
```
2. Lấy tất cả quiz theo phân loại
- Endpoint: **GET** `/api/v1/quizzes/:category`
```json
# same as above
```
3. Lấy một quiz cụ thể theo id cho user làm
- Endpoint: **GET** `/api/v1/quizzes/:id`
```json
{

  "id": "quiz123",

  "title": "CPR Knowledge Test",

  "description": "Test your knowledge of CPR techniques",

  "category": "cpr",

  "difficulty": "beginner",

  "timeLimit": 600,

  "questions": [

    {

      "id": "q1",

      "text": "What is the correct compression rate for adult CPR?",

      "options": [

        "60-80 compressions per minute",

        "100-120 compressions per minute",

        "140-160 compressions per minute",

        "As fast as possible"

      ],

      "answer": -1  // Correct answer is hidden

    },

    ...

  ]

}
```
### Kết quả trả về của AI model, thực hiện request đến AI model trong AI service
