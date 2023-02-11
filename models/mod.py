import cv2
import torch


class MiDas():
    def __init__(self, models_name: str = "DPT_Hybrid", photo_pth: str = ''):
        self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        self.models_name = models_name
        self.photo_pth = photo_pth

        self.__load_model()
        self.__load_photo()
        self.__save_res_photo()

    def __load_model(self) -> None:
        self.midas = torch.hub.load('intel-isl/MiDas', self.models_name)
        self.midas.to(self.device)
        self.midas.eval()

        midas_transforms = torch.hub.load('intel-isl/MiDas', 'transforms')

        if self.models_name == "DPT_Large" or self.models_name == "DPT_Hybrid":
            self.transform = midas_transforms.dpt_transform
        else:
            self.transform = midas_transforms.small_transform

    def __load_photo(self) -> None:
        self.img = cv2.imread(self.photo_pth)
        self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)

        self.input_batch = self.transform(self.img).to(self.device)

    def __save_res_photo(self) -> None:
        with torch.no_grad():
            prediction = self.midas(self.input_batch)

            prediction = torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=self.img.shape[:2],
                mode="bicubic",
                align_corners=False,
            ).squeeze()

        output = prediction.cpu().numpy()

        cv2.imwrite('./data/midas.png', output)
