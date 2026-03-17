-- Bảng 1: Lưu thông tin 6 ảnh camera (View)
CREATE TABLE Scenes (
    SceneID INT PRIMARY KEY IDENTITY(1,1),
    SampleToken VARCHAR(100) UNIQUE,
    ImgPath_Front NVARCHAR(255),
    ImgPath_Back NVARCHAR(255),
    ImgPath_FrontLeft NVARCHAR(255),
    ImgPath_FrontRight NVARCHAR(255),
    ImgPath_BackLeft NVARCHAR(255),
    ImgPath_BackRight NVARCHAR(255)
);

-- Bảng 2: Lưu nhãn và trạng thái CRUD
CREATE TABLE Annotations (
    AnnoID INT PRIMARY KEY IDENTITY(1,1),
    SampleToken VARCHAR(100),
    Category NVARCHAR(50),
    X_Coord FLOAT, Y_Coord FLOAT, Width FLOAT, Height FLOAT,
    ReviewStatus INT DEFAULT 0, -- 0: Chưa xem, 1: Đúng, 2: Sai
    Note NVARCHAR(MAX),
	ReviewDate DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_Scene FOREIGN KEY (SampleToken) REFERENCES Scenes(SampleToken)
);

-- Bảng 3: Tạo bảng lưu số lượng đối tượng đã được kiểm tra
CREATE TABLE ObjectLabels (
    ObjID INT PRIMARY KEY IDENTITY(1,1),
    SampleToken VARCHAR(100),
    Category VARCHAR(50),
    InstanceToken VARCHAR(100),
    CONSTRAINT FK_Object_Scene FOREIGN KEY (SampleToken) REFERENCES Scenes(SampleToken)
);

drop table Scenes
drop table Annotations

select * from Scenes
select * from Annotations
