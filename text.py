from flask import Flask, request, jsonify
app = Flask(__name__)
@app.route('/lpr/callback', methods=['POST'])
def lpr_callback():    
data = request.get_json()    
# 校验Token或签名    
plate = data['plate_number']    
ts = data['timestamp']    
# 业务处理：存库或比对白名单/黑名单    
return jsonify({'status':'ok'}), 200
if __name__ == '__main__':    
app.run(host='0.0.0.0', port=443, ssl_context=('cert.pem','key.pem'))