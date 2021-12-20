from typing import Tuple
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from datetime import datetime
import random

# Create your views here.
import mysql.connector



item_count = 0
user = {}
cart = {}
total = 0
user = {}
owner = 0

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="130301",
  database="bookstore"
)
mycursor = mydb.cursor(dictionary = True)
def home_page(request,*args,** kwargs):
    

    #sql = "INSERT INTO Report (Sale, Expenditure, Date) VALUES (123.12, 122.11,'2021-12-18')"
   # mycursor.execute(sql)

    #mydb.commit()
    
    return  render(request,"home_page.html",{})


def userSign(request,*args,**kwargs):
    
    return render(request,"user_signin.html",{"status":"","signed":""})


def user_profile(request,*args,**kwargs):
    global user
    username = request.POST['username']
    password = request.POST['password']
    values = (username,password,)
    sql =  "Select * from user Where Username = %s and Password = %s"
    mycursor.execute(sql,values)
    result = mycursor.fetchall()

    if(result == []):
        return render(request,"user_signin.html",{"status":"Wrong credentials","signed":""})

    result = result[0]
    user = result
    return render(request,"user_profile.html",result)


def search(request, *args,**kwargs):
    return render(request,"search.html",{})


def results(request,*args,**kwargs):
    isbn = request.POST["ISBN"]
    genre = request.POST["genre"]
    author = request.POST["Author"]
    title = request.POST["Title"]
    sql = "Select Title,ISBN from book where"
    values = []
    check = 0
    if(genre != 'Any'):
        sql += " Genre like %s"
        values.append(genre)
        check +=1

    if(isbn != ''):
        if(check>0):
            sql += " and"
        sql += " ISBN = %s"
        values.append(isbn)
        #print(values)
        check +=1
    
    if(author != ''):
        if(check>0):
            sql += " and"
        sql += " Author like %s"
        author = "%" + author
        author = author + "%"
        values.append(author)
        check+=1

    if(title != ''):
        if(check>0):
            sql += " and"
        sql += " Title like %s"
        title = "%" + title
        title = title + "%"
        values.append(title)
        check+=1
    
    if(len(values)==0):
        sql = "Select * from book"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
    else:
        values = tuple(values)
        print(sql,values)
        mycursor.execute(sql,values)
        myresult = mycursor.fetchall()

    dictionary = {}
    for i in range(len(myresult)):
        dictionary[i] = myresult[i]
    dict2 = {}
    dict2["Books"] = dictionary
    return render(request,"result.html",dict2)


def book_page(request,*args,**kwargs):
    global owner
    isbn =request.GET["ISBN"]
    sql = "Select * from book where ISBN = " + isbn
    mycursor.execute(sql)
    result = mycursor.fetchall()
    result = result[0]

    sql = "Select * from publisher where Id = "+str(result["Publisher"])
    mycursor.execute(sql)
    result2 = mycursor.fetchall()
    result2 = result2[0]

    sql = "Select Title,ISBN from book where (Author = '"+result["Author"]+"' or Genre = '"+result["Genre"]+"' ) and ISBN <> '"+str(result["ISBN"])+"'"
    mycursor.execute(sql)
    tempR = mycursor.fetchall()
    if(len(tempR)>5):
        tempR = tempR[:5]

    temp2 = {}
    for i in range(len(tempR)):
        temp2[i] = tempR[i]

    d = {}
    d["Book"] = result
    d["Publisher"] = result2
    d["Cart"] = {"quantity" : 0}
    d["Owner"] = {"Owner":owner}
    d["Similar"] = temp2
    for item in cart.values():
        if(item["ISBN"] == isbn):
            d["Cart"] = {"quantity":item["Quantity"]}
    
    return render(request,"book.html",d)

def add(request,*args,**kwargs):
    global cart
    global item_count
    isbn = request.GET["ISBN"]
    check =0
    for item in cart.values():
        if(item["ISBN"] == isbn):
            item["Quantity"] +=1
            check = 1
        
    
    if(check == 0):

        cart[item_count] = {"ISBN":isbn , "Quantity":1}
    item_count +=1 
    print(cart)

    return redirect(request.META.get('HTTP_REFERER'))


def show_cart(request,*args,**kwargs):
    global cart
    global total
    total = 0
    i =0 
    #print(cart)
    result = {}
    for item in cart.values():
        sql = "Select Title,ISBN,Price from book where ISBN = " + item["ISBN"]
        mycursor.execute(sql)
        temp = mycursor.fetchone()
       # print(temp)
        result[i]= {item["Quantity"] :temp}
        total += (temp["Price"] * item["Quantity"])
        i +=1
    
    result2 = {}
    result2["Books"] = result
    result2["Total"] = total
    #print(result)
    return render(request,"cart.html",result2)



def checkout(request,*args,**kwargs):
    global cart 
    global item_count
    global total
    global user
    order_no = "OR"
    result = "not"
    temp = 0
    while(result != []):
        temp = random.randint(100,10000)
        sql = "Select ID from orders where ID = '"+order_no+str(temp)+"'"
        print(sql)
        mycursor.execute(sql)
        result = mycursor.fetchall()

    order_no = order_no + str(temp)
    if(len(user)!=0):
        Today = datetime.today().strftime('%Y-%m-%d')
        for item in cart.values():
            sql = "Update book Set Stock = Stock -" + str(item["Quantity"]) + " where ISBN = '" + item["ISBN"] + "'"
            #print(sql)
            mycursor.execute(sql)
            mydb.commit()
            #print("line 209")
            sql = "Insert into Orders(ID,Book_ISBN,Quantity,Address,Postal,Province,Order_placed_on) values(%s,%s,%s,%s,%s,%s,%s)"
            if(request.POST["Address"]!=''):
                mycursor.execute(sql,(order_no,item["ISBN"],str(item["Quantity"]),request.POST["Address"],request.POST["Postal"],request.POST["Province"],Today))   
            else:
                mycursor.execute(sql,(order_no,item["ISBN"],str(item["Quantity"]),user["Address"],user["Postal"],user["Province"],Today))

            mydb.commit()
        
        sql = "Select * from Report where Date = '"+ Today + "'"
        mycursor.execute(sql)
        result2 = mycursor.fetchall()
        #print(result2)
        if(len(result2) == 0):
            sql = "Insert into Report(Sale,Date) values("+str(total)+",'" +Today+"')"
        else:
            sql = "Update Report Set Sale = Sale + "+str(total) +" where Date = '"+Today + "'"
        
        print(sql)
        mycursor.execute(sql)
        mydb.commit()
        cart = {}
        item_count = 0
        total = 0
        return render(request,"order_placed.html",{"number":order_no})
    else:
        return render(request,"user_signin.html",{"status":"","signed":"You must sign in to check out"})


def track(request,*args,**kwargs):
    result = {}

    result["status"] = 0
    result["order"] = 0
    result["note"] = ""
    return render(request,"track_order.html",result)


def track_order(request,*args,**kwargs):
    sql = "Select * from orders where ID = '"+ request.POST["Order"] + "'"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    if(len(result) == 0):
        result2 = {}
        result2["status"] = 0
        result2["note"] = "No order found"
        result2["order"] = ''
        return render(request,"track_order.html",result2)
    else:
        resultD = {}
        result2 ={}
        temp={}
        for i in range(len(result)):
            sql = "Select Title from book where ISBN = '"+str(result[i]["Book_ISBN"]) + "'"
            mycursor.execute(sql)
            resultD = mycursor.fetchall()
            resultD = resultD[0]["Title"]
            temp[i] = {resultD : result[i]["Quantity"]}

        result2["order"] = temp
        result2["Date"] = result[0]["Order_placed_on"]
        result2["Address"] = result[0]["Address"]
        result2["Province"] = result[0]["Province"]
        result2["Postal"] = result[0]["Postal"]
        result2["Status"] = 1    
        result2["note"] = ''

        print(result2)
        return render(request,"track_order.html",result2)


def signOwner(request,*args,**kwargs):
    global user
    global owner
    username = request.POST["username"]
    password = request.POST["password"]
    user = {}
    sql = "Select * from owners where Username = %s and Password = %s"
    values = (username,password)
    mycursor.execute(sql,values)
    result = mycursor.fetchall()
    if(len(result)==0):
        return render(request,"owner_signin.html",{"status":"Wrong Credentials"})
    else:
        result = result[0]
        
        owner = 1
        return render(request,"report.html",{})


def owner_auth(request,*args,**kwargs):
    return render(request,"owner_signin.html",{})



def removeBook(request,*args,**kwargs):
    deleteI = request.GET["ISBN"]

    sql = "Delete from book where ISBN = '"+deleteI+"'"
    mycursor.execute(sql)
    mydb.commit()
    return render(request,"search.html",{})


def expenditure(request,*args,**kwargs):
    result2 = {}
    if(request.POST["date"] == ''):
        result2["error"] = "Please provide Date"
        return render(request,"report.html",result2)
        
    sql = "Select * from Report where Date = '"+request.POST["date"] + "'"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    result = result[0]
    
    result2["status"] = 1
    result2["error"] = ""
    result2["report"] = result
    return render(request,"report.html",result2)

def authorR(request,*args,**kwargs):
    sql = "select sum(book.Price * orders.Quantity) as Sale,book.Author as Author from book,orders where orders.Book_ISBN = book.ISBN group by book.Author"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    temp= {}
    for i in range(len(result)):
        temp[i] = result[i]

    result2 = {}
    result2["status"] = 2
    result2["error"] = ""
    result2["report"] = temp
    return render(request,"report.html",result2)


def genreR(request,*args,**kwargs):
    sql = "select sum(book.Price * orders.Quantity) as Sale,book.Genre as Genre from book,orders where orders.Book_ISBN = book.ISBN group by book.Genre"
    mycursor.execute(sql)
    result = mycursor.fetchall()
    temp= {}
    for i in range(len(result)):
        temp[i] = result[i]

    result2 = {}
    result2["status"] = 3
    result2["error"] = ""
    result2["report"] = temp
    return render(request,"report.html",result2)