# 🧠 AWS AI Orchestrator

Plataforma completa para la **orquestación y despliegue de modelos de Inteligencia Artificial** en la nube de **Amazon Web Services (AWS)**.  
Este proyecto integra infraestructura automatizada con **Terraform**, un backend modular basado en **microservicios FastAPI** y un **frontend en Vue.js**.

---

## 🚀 Arquitectura General

La aplicación se compone de tres módulos principales:

### 🏗️ 1. Infraestructura como código (Terraform)
Define y despliega toda la infraestructura necesaria en AWS:
- **Amazon ECS**: ejecución de microservicios en contenedores Docker.
- **Amazon ECR**: almacenamiento de imágenes Docker.
- **Amazon Cognito**: autenticación de usuarios y emisión de tokens JWT.
- **Amazon S3** + **CloudFront**: hosting del frontend y distribución global.
- **Amazon API Gateway**: exposición pública de los endpoints.
- **Amazon CloudWatch**: monitorización centralizada de logs y errores.
- **Amazon WAF** y **IAM Roles**: seguridad y control de acceso.
- **Amazon SageMaker** y **Athena**: soporte para la ejecución y análisis de modelos.

Cada recurso se encuentra organizado en módulos independientes dentro del directorio `iac/`, facilitando la escalabilidad y reutilización.

---

### ⚙️ 2. Backend — Microservicios con FastAPI
El backend está diseñado bajo un enfoque **microservicial**, donde cada modelo de IA se implementa como un servicio independiente dentro de **Amazon ECS**. Se encuentra dentro del directorio `backend/`.

#### Microservicios incluidos:
- **Orchestrator API**: coordina las peticiones del frontend y gestiona la comunicación entre microservicios.
- **Upscaling API**: mejora de resolución de imágenes mediante *Real-ESRGAN*.
- **Denoising API**: eliminación de ruido utilizando modelos basados en *DeepInv*.
- **Inpainting API**: reconstrucción de zonas faltantes o deterioradas en imágenes con *PaddleOCR* y *Lama*.

Cada API:
- Se implementa con **FastAPI**.
- Está protegida mediante autenticación **JWT** de **Amazon Cognito**.
- Se prueba con **pytest** y **tox**, garantizando una cobertura mínima del 85%.

---

### 💻 3. Frontend — Vue.js
Interfaz interactiva desarrollada en **Vue.js**, desplegada en **Amazon S3** y distribuida globalmente con **CloudFront**. Se encuentra dentro del directorio `frontend/`.

Características principales:
- Selector de modelos: Upscaling, Denoising o Inpainting.
- Subida de imágenes con vista previa y ajuste automático de orientación.
- Envío de peticiones a `/image-ai-analysis` para procesar las imágenes.
- Visualización comparativa y descarga del resultado final.
- Autenticación automática a través del endpoint `/authorize`, que obtiene el token JWT de **Cognito** para cada sesión.

---