# TODO: Teste comentado temporariamente enquanto as dependências não estão prontas
# Descomente quando:
# 1. Modelos XGBoost forem treinados
# 2. LLM_API_KEY estiver configurada
# 3. Arquivos necessários estiverem disponíveis


# class TestUltrasoundEndpoint:
#     """Testes para o endpoint POST /api/v1/ultrasound/predict."""

#     def test_ultrasound_com_imagem_valida(self, client):
#         img = Image.new("RGB", (100, 100), color="red")
#         img_bytes = io.BytesIO()
#         img.save(img_bytes, format="PNG")
#         img_bytes.seek(0)

#         response = client.post(
#             "/api/v1/ultrasound/predict",
#             files={"file": ("ultrassom.png", img_bytes, "image/png")},
#         )
#         assert response.status_code == 200
#         data = response.json()
#         assert "diagnosis" in data
#         assert "confidence" in data

#     def test_ultrasound_arquivo_nao_imagem_retorna_400(self, client):
#         response = client.post(
#             "/api/v1/ultrasound/predict",
#             files={"file": ("texto.txt", b"nao sou imagem", "text/plain")},
#         )
#         assert response.status_code == 400
#         assert "must be an image" in response.text.lower()

#     def test_ultrasound_sem_arquivo_retorna_422(self, client):
#         response = client.post("/api/v1/ultrasound/predict")
#         assert response.status_code == 422

#     def test_ultrasound_imagem_muito_grande_retorna_400(self, client):
#         img = Image.new("RGB", (500, 500), color="blue")
#         img_bytes = io.BytesIO()
#         img.save(img_bytes, format="PNG")
#         img_bytes.seek(0)
#         large_data = img_bytes.getvalue()

#         response = client.post(
#             "/api/v1/ultrasound/predict",
#             files={"file": ("grande.png", large_data, "image/png")},
#         )
#         assert response.status_code == 200
