
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from time import sleep
import pandas as pd


def config_browser():
   # Configuración
   opts = Options()
   opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

   # Instala el web driver automáticamente
   driver = webdriver.Chrome(
      service=Service(ChromeDriverManager().install()),
      options=opts )  
   
   return driver

 #La funcion refresh_page se creo debido a un bug de que la pagina no se abre correctamente

#Recarga la pagina si no encuentra los elementos 
def refresh_page(driver, element_name, element_price):
   elementos_encontrados = False
   
   for i in range(3):
      if elementos_encontrados == True:
         #Si encontro los elementos termina el bucle
         break       
      try:
      #Espera hasta 5 segundos a que se encuentren los elementos
         WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, element_name)))
         WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, element_price)))
         elementos_encontrados = True
       #Si no encuentra los elementos, recarga la pagina   
      except TimeoutException:       
         driver.refresh()
         
            
         
# Desplaza la ventana del navegador un tercio hacia abajo
def desplazamiento(web_driver):
   total_height = web_driver.execute_script("return document.body.scrollHeight")
   scroll_height = total_height // 3
   web_driver.execute_script("window.scrollTo(0, {})".format(scroll_height))

        
#Obtiene el nombre y precio de cada producto
def get_products(url_page, element_name, element_price):
    productos = []
    driver = config_browser()
    wait = WebDriverWait(driver, 10)  # Espera explícita
    
   # Itera sobre cada página y obtiene los nombres y precios de productos
    for page_number in range(1, 3):
        url = url_page.format(page_number)
        driver.get(url)
               
        sleep(3)
        
        try:
            refresh_page(driver, element_name, element_price)        
        except TimeoutException:
            print("No se encontraron elementos luego de 3 intentos.")
            
        desplazamiento(driver)       
        sleep(2) # Espera para que carguen los nuevos elementos
        
        # Verifica la presencia de los elementos
        try:
            wait.until(EC.presence_of_all_elements_located((By.XPATH, element_name)))
            wait.until(EC.presence_of_all_elements_located((By.XPATH, element_price)))
        except TimeoutException:
            print("Elementos no encontrados en la página actual. Saltando a la siguiente página...")
            #pasa a la siguiente iteracion
            continue
        
        titulos = driver.find_elements(By.XPATH, element_name)
        precios = driver.find_elements(By.XPATH, element_price)
        
        # Recorre las 2 listas al mismo tiempo
        for titulo, precio in zip(titulos, precios):
            productos.append({'Nombre': titulo.text, 'Precio': precio.text})
    
    driver.quit()  # Asegurarse de cerrar el navegador al finalizar
    
    return productos


# Ejemplo de uso
xpath_title = "//span[@class='vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body']"
xpath_price = "//span[@class='valtech-carrefourar-product-price-0-x-currencyContainer']"
url_yerba = "https://www.carrefour.com.ar/Desayuno-y-merienda/Yerba?page={0}"

productos = get_products(url_yerba, xpath_title, xpath_price)
print(productos)
