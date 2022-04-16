# Venkata Satya Yaswanth Tondepu 
# CSE 6331 sec 1
# Assignment 6
from socket import socket
from flask import Flask, render_template,request, redirect, url_for
import pyodbc
import random
from random import randint
from flask_socketio import SocketIO, emit,send




app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

server = 'yaswanth.database.windows.net'
database = 'assgn2'
username = 'yaswanth'
password = 'Yashu@267,.'   
driver= '{ODBC Driver 17 for SQL Server}'


@app.route('/')
def home():
   return render_template('home.html')

def createNewRoom():
   room_id = randint(100000,999999)
   return room_id
@app.route("/wait", methods=['POST','GET'])
def homeform():
   playerName = request.form['playerName']
   print(playerName)
   cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
   cursor = cnxn.cursor()
   cursor.execute("SELECT roomCode FROM a6 where isFull = 0")
   rows = cursor.fetchall()
   if len(rows) == 0:
      roomCode = createNewRoom()
      cursor.execute("SELECT roomCode FROM a6")
      rows1 = cursor.fetchall()
      while roomCode in rows1:
         roomCode = createNewRoom()
      cursor.execute("INSERT INTO a6 (roomCode,player1) VALUES (?,?)",(roomCode,playerName))
      cnxn.commit()
      role = "player1"
      return render_template('wait.html',playerName=playerName,roomCode=roomCode,role=role)
   else:
      roomCode = rows[0][0]
      print(roomCode)
      cursor.execute("SELECT player2 FROM a6 where roomCode = ?",(roomCode,))
      rows1 = cursor.fetchall()
      if rows1[0][0] is None:
         cursor.execute("UPDATE a6 SET player2 = ? WHERE roomCode = ?",(playerName,roomCode))
         cnxn.commit()
         role = "player2"
         return render_template('wait.html',playerName=playerName,roomCode=roomCode,role=role)
      else:
         cursor.execute("UPDATE a6 SET admin = ?, isfull=? WHERE roomCode = ?",(playerName,1,roomCode))
         cnxn.commit()
         role = "admin"
         return render_template('admin.html',playerName=playerName,roomCode=roomCode,role=role)

@app.route("/game/<roomCode>/<role>", methods=['POST','GET'])
def setGameSettings(roomCode,role):
   pile1 = request.form['pile1']
   pile2 = request.form['pile2']
   pile3 = request.form['pile3']
   min = request.form['min']
   max = request.form['max']
   firstPlayer = request.form['firstPlayer']
   cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
   cursor = cnxn.cursor()
   cursor.execute("UPDATE a6 SET pile1 = ?, pile2 = ?, pile3 = ?, min = ?, max = ?,firstPlayer = ?  WHERE roomCode = ?",(pile1,pile2,pile3,min,max,firstPlayer,roomCode))
   cnxn.commit()
   cursor.execute("SELECT player1 FROM a6 where roomCode = ?",(roomCode,))
   rows = cursor.fetchall()
   player1 = rows[0][0]
   cursor.execute("SELECT player2 FROM a6 where roomCode = ?",(roomCode,))
   rows1 = cursor.fetchall()
   player2 = rows1[0][0]
   socketio.emit('start-game',{'roomCode':roomCode})
   return render_template('game-admin.html',roomCode=roomCode,pile1=pile1,pile2=pile2,pile3=pile3,min=min,max=max,player1=player1,player2=player2,role=role)

@app.route("/delcareWinner", methods=['POST','GET'])
def delcareWinner():
   roomCode = request.form['roomCode']
   winner= request.form['winner']
   player1 = request.form['player1']
   player2 = request.form['player2']
   cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
   cursor = cnxn.cursor()
   cursor.execute("UPDATE a6 SET winner = ? WHERE roomCode = ?",(winner,roomCode))
   cnxn.commit()
   if winner == "player1":
      name=player1
   else:
      name=player2
   return render_template('game-admin.html',roomCode=roomCode,name=name,gameOver=False)

@socketio.on('start-game')
def startGame(data):
   print("app.py startGame")
   roomCode = data['roomCode']
   role = data['role']
   socketio.emit("test",{'roomCode':roomCode,'role':role})
   return redirect(url_for('gamePlayer',roomCode=roomCode,role=role))   

@app.route("/gamePlayer/<roomCode>/<role>", methods=['POST','GET'])
def gamePlayer(roomCode,role):
   cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
   cursor = cnxn.cursor()
   cursor.execute("SELECT * FROM a6 where roomCode = ?",(roomCode,))
   rows = cursor.fetchall()
   player1 = rows[0][1]
   player2 = rows[0][2]
   pile1 = rows[0][5]
   pile2 = rows[0][6]
   pile3 = rows[0][7]
   min = rows[0][8]
   max = rows[0][9]
   firstPlayer = rows[0][13]
   role=role
   return render_template('game-player.html',roomCode=roomCode,pile1=pile1,pile2=pile2,pile3=pile3,min=min,max=max,player1=player1,player2=player2,role=role,turn=firstPlayer)

@app.route("/gamePlayer/<roomCode>/<role>/removeStones", methods=['POST','GET'])
def removeStones(role,roomCode):
   # roomCode = request.form['roomCode']
   role = request.form['role']
   print(role)
   pile = int(request.form['pile'])
   stones = int(request.form['stones'])
   cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
   cursor = cnxn.cursor()
   cursor.execute("SELECT * FROM a6 where roomCode = ?",(roomCode,))
   rows = cursor.fetchall()
   pile1 = rows[0][5]
   pile2 = rows[0][6]
   pile3 = rows[0][7]
   min = rows[0][8]
   max = rows[0][9]
   player1 = rows[0][1]
   player2 = rows[0][2]

   if role=="player1":
      turn="player2"
   else:
      turn="player1"
  
   if pile == 1:
      newPile = pile1- stones
   elif pile == 2:
      newPile = pile2- stones
   elif pile == 3:
      newPile = pile3- stones
   print("newPile: "+str(newPile))
   if newPile>=0:
      cursor.execute("UPDATE a6 SET pile"+str(pile)+" = ? WHERE roomCode = ?",(newPile,roomCode))
      cnxn.commit()
      cursor.execute("SELECT * FROM a6 where roomCode = ?",(roomCode,))
      rows = cursor.fetchall()
      player1 = rows[0][1]
      player2 = rows[0][2]
      pile1 = rows[0][5]
      pile2 = rows[0][6]
      pile3 = rows[0][7]
      min = rows[0][8]
      max = rows[0][9]
      socketio.emit('update-pile',{'roomCode':roomCode,'turn':turn,'pile1':pile1,'pile2':pile2,'pile3':pile3,'pile':pile,'stones':stones})

      return render_template('game-player.html',roomCode=roomCode,pile1=pile1,pile2=pile2,pile3=pile3,min=min,max=max,player1=player1,player2=player2,role=role,turn=turn)
   else:
      pile1 = rows[0][5]
      pile2 = rows[0][6]
      pile3 = rows[0][7]
      return render_template('game-player.html',roomCode=roomCode,pile1=pile1,pile2=pile2,pile3=pile3,min=min,max=max,player1=player1,player2=player2,role=role,error="You can't remove more stones than you have",turn=role)

@app.route("/game/<roomCode>/declareWinner", methods=['POST','GET'])
def declareWinner(roomCode):
   winner = request.form['winner']
   cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
   cursor = cnxn.cursor()
   cursor.execute("UPDATE a6 SET winner = ? WHERE roomCode = ?",(winner,roomCode))
   cursor.execute("SELECT * FROM a6 where roomCode = ?",(roomCode,))
   rows = cursor.fetchall()
   player1 = rows[0][1]
   player2 = rows[0][2]
   pile1 = rows[0][5]
   pile2 = rows[0][6]
   pile3 = rows[0][7]
   min = rows[0][8]
   max = rows[0][9]
   role = 'admin'
   socketio.emit('game-over',{'roomCode':roomCode,'winner':winner,'player1':player1,'player2':player2,'pile1':pile1,'pile2':pile2,'pile3':pile3})
   return render_template('game-admin.html',roomCode=roomCode,pile1=pile1,pile2=pile2,pile3=pile3,min=min,max=max,player1=player1,player2=player2,role=role,turn='player1',gameOver=True,winner=winner)



if __name__ == '__main__':
    socketio.run(app, debug=True)
    