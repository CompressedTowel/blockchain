import binascii
import hashlib
import json
import time
from argparse import ArgumentParser
from urllib.parse import urlparse
from flask import Flask, request, jsonify
from blockchain.functions.blockchain import *
from blockchain.functions.Account import *

blockchain = BlockChain()
blockchain.genesis_block()
app = Flask(__name__)
print(blockchain.hash(blockchain.blockchain[0]))

# 交易验证交给API内部来处理
########################################
#这里api还挺麻烦的，写的时候可能需要两边对接下
########################################


@app.route("/AddNewBlock", methods=["POST"])
def AddNewBlock():
    #这里传入的block是一条区块链
    block = request.get_json()
    # 还应该检查block的格式
    if blockchain.TheBlokCheck(block):
        # 格式确认
        if blockchain.add_block(block):
            # 区块确认
            msg = "挖矿成功"
            print(msg)
            Award_Transaction = {
                "inputs": {
                    "index": len(blockchain.transaction) + 1,  # 变量名和函数名不要同名，否则会引起冲突
                    "sender_signature": 0,
                    "transaction_reference:": "NULL"
                },
                "outputs": {
                    "amount": blockchain.TheBlockAward,
                    "recipient": "recipident"
                },
                "Fees": 0
            }
            blockchain.transaction.append(Award_Transaction)  # 只有这一步是必须的，后面的返回值可以修改
            #这条交易信息直接加入所有人的计算表单

            value = {"msg": msg,
                     "Award_Transaction": Award_Transaction}
            return jsonify(value), 200
        else:
            msg = "错误区块"
            return msg, 200
    else:
        return "区块格式错误", 200

@app.route("/chain")#该API可以直接访问所有区块
def chain():
    return jsonify(blockchain.blockchain),200

@app.route('/PreHash',methods=['GET'])
def prehash():
    last_block = blockchain.blockchain[-1]
    return blockchain.hash(last_block),200

@app.route('/transaction',methods=['Get'])
def TransactionInfo():#返回所有交易信息
    pass

@app.route('/nodes/register',methods=['POST'])
def register_node():
    values = request.get_json()
    nodes = values.get('nodes')
    if len(nodes) == 0:
        return "Error: Please supply a valid list of nodes", 400
    for node in nodes:
        blockchain.register_node(node)
    response = {
        'msg':"New nodes added!",
        'nodes':list(blockchain.nodes)
    }
    return jsonify(response)
#测试时使用的json文件为
#{"nodes":["","",""]}

@app.route("/LongChain",methods=['GET'])
def longchain():
    replaced = blockchain.longest_chain()
    if replaced:
        response={
            'msg':"This chain was replaced!",
            "new_chain":blockchain.blockchain
        }
    else:
        response={
            'msg': "This chain is the longest!",
            "new_chain": blockchain.blockchain
        }
    return jsonify(response),200

@app.route("/tx/merkleroot",methods=['GET'])
def TxRoot():#使用方法——输入交易返回最终root值
    tx = request.get_json()
    return blockchain.MerkleRoot(tx)
@app.route("/AcCreate",methods=['GET'])
def AcCreate():
    '''
    传入json
    {
    "id":id --传入用户名
    '''
    id = request.get_json()['id']
    private_key = GenSk()
    publick_key = GenPk(private_key)
    try:
        adress = AdCre(private_key,id)
    except Exception as e:
        return e
    response = {
        "sk":binascii.hexlify(private_key).decode(),
        "pk":binascii.hexlify(publick_key).decode(),
        "adress":adress,
        "WARNING!":"请保存好你的私钥！"
    }
    return jsonify(response)

@app.route("/tx/publish",methods=['POST'])
def TxPublish():
    #返回对交易的签名
    '''
    {
    "private_key":,
    "sender_adress":,
    "amount":,
    "Fees":
    }
    :return:
    '''
    value = request.get_json()#得到表单中的数据
    sk = binascii.unhexlify(value['private_key'])
    pk = GenPk(sk) # 生成公钥
    #现在生成的sk与pk都是字节串格式
    db = pymysql.connect(host="localhost", port=3306, user="root", passwd="123456", db="blockchain")
    cursor = db.cursor()
    sql = 'select adress from pkadress where adress="{}"'.format(value['sender_adress'])
    sql1 = 'select adress from pkadress where adress="{}"'.format(value['recipient'])
    cursor.execute(sql)
    result1 = cursor.fetchone()
    cursor.execute(sql1)
    result2 = cursor.fetchone()
    if (result1 or result2) == None:
        cursor.close()
        db.close()
        return "Account Not Exist!"
    else:
        sql2 = 'select tx_nonce from pkadress where adress="{}"'.format(value['sender_adress'])
        cursor.execute(sql2)
        tx_nonce = cursor.fetchone()[0]
        data = {
            "inputs": {
                "sender_adress": value['sender_adress'],
                "tx_nonce":tx_nonce+1,
            },
            "outputs": {
                "amount": value['amount'],
                "recipient":value['recipient'],
                "Fees":value['Fees']
            }
        }
        Sig = GenSig(sk,str(data))
        cursor.close()
        db.close()
        return Sig,200

new_transaction ={
  "index": 1,
  "data": {
  "inputs": {
    "sender_adress": "16mUgTDy7A85PXumPKnn1EY2vpU5kt7J3r",
    "tx_nonce": 1
  },
  "outputs": {
    "amount": 12,
    "recipient": "1M5gkaXnCebVND7SDeUyGTKhx5N3C2DDgL",
     "Fees": 1
  }
},
  "signature": "1c8c884a69aa985b868233a964cc2e9f81d4c1495a7aff6fb912c9d76d763374e930b38b2ecf5d8d5459ffc3e2d1c248d1fbb8d9ae32817b3987491c3117c26f"
}





if __name__ == "__main__":
    app.run()
    '''
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    app.run(debug=True, host='0.0.0.0', port=5000)
    '''