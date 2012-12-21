# pagseguro-tornado-testserver

Servidor de testes do pagseguro escrito em tornado web server.

***

## Rodando o aplicativo

Em primeiro lugar você deve instalar o tornado com o comando: 
    
    pip install -r requirements.txt


Após instalado, rode o servidor com o seguinte comando:
    
    sudo python app.py --return_url=sua-url-de-retorno
    

Lembre-se de mapear a url do pagseguro para o seu endereço de localhost, edite o arquivo /etc/hosts e inclua a seguinte linha:
    
    127.0.0.1 pagseguro.uol.com.br