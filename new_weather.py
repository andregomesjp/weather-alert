if __name__ == "__main__":

    import requests
    import smtplib
    import ssl
    from email.message import EmailMessage
    import geocoder
    from sys import exit

    with open("api.txt", "r") as f:
        API_KEY = f.readline()  # Chave da API para consulta
    BASE_URL = "https://api.openweathermap.org/data/2.5/onecall"  # URL base para request das informações climáticas do dia
    GEOCODING_URL = "http://api.openweathermap.org/geo/1.0/reverse"  # URL base para request da localização geográfica (latitude e longitude) da cidade onde será criado o alerta

    # Obtenção das coordenadas de latitude e longitude
    g = geocoder.ip("me")
    lat = g.latlng[0]
    lon = g.latlng[1]
    request_geo = f"{GEOCODING_URL}?lat={lat}&lon={lon}&limit=1&appid={API_KEY}"  # Complemento para o request da localização geográfica
    response_geo = requests.get(request_geo)

    if response_geo.status_code == 200:
        city = response_geo.json()[0]["name"]
    else:
        print("Ocorreu um erro.")
        exit()

    # Request da previsão do tempo do dia (excluindo previsão atual, por minuto e por hora), no sistema métrico e em português
    request_url = f"{BASE_URL}?lat={lat}&lon={lon}&units=metric&lang=pt_br&exclude=current,minutely,hourly&appid={API_KEY}"
    response = requests.get(request_url)

    if response.status_code == 200:
        data = response.json()
        try:
            alertas = data["alerts"][0]["description"]  # Isolando a descrição do alerta
            send = True
        except:
            send = False
            pass
    else:
        print("Ocorreu um erro.")
        exit()

    if send:
        subject = f"Alerta de tempestade em {city.capitalize()}!"  # Mensagem que aparecerá como Assunto do email
        body = alertas
        sender_email = "alertatempestadeapp@gmail.com"  # Email que enviará o alerta (Deverá permitir acesso à app menos seguro)
        receiver_email = "alertatempestadeapp@gmail.com"  # Email que receberá o alerta
        with open("password.txt", "r") as f:
            password = f.readline()  # Senha do email que enviará o alerta

        message = EmailMessage()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject

        html = f"""
        <html>
            <body>
                <h1>{subject}</h1>
                <p>{body}</p>
            </body>
        </html>
        """

        message.add_alternative(html, subtype="html")

        context = ssl.create_default_context()
        print("Enviando Email")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        print("Email Enviado")
    else:
        print("Não há alertas hoje para esta localização.")
