package main
import (
	"database/sql"
	"fmt"
	_ "github.com/go-sql-driver/mysql"
	"math/rand"
	"time"
)
func main() {	
	rand.Seed( time.Now().UnixNano())
	name := [6]string{"Tat","Dad","cat", "dog", "mad", "goat"}
	age  := [6]int{5, 6, 4, 6, 3,10}
	// db,_:= sql.Open("mysql", "root:tatvam@/openhack")
	db,_:= sql.Open("mysql", "shubug:Thumbsdown7320#@tcp(openhack-flydata.cdvbjpsetxhz.ap-southeast-1.rds.amazonaws.com:3306)/openhack")
	fmt.Println(db)	

	stmtCrTa,err := db.Prepare("create table us (" +
		"Id decimal(5,0) UNIQUE NOT NULL," +
		"Name varchar(50) NOT NULL, " +
		"Age decimal(5,0) NOT NULL, " +
		"Comapany varchar(255) NOT NULL" +
		")")

	if err != nil {
		panic(err.Error())
	}	
	_,err = stmtCrTa.Exec()
	if err != nil {
		panic(err.Error())
	}

	stmtIn,err := db.Prepare("INSERT INTO us values(?, ?, ?, ?)")	
	if err != nil {
		panic(err.Error())
	}	
	stmtOut,err := db.Prepare("Select * from us where Id = ?")	
	if err != nil {
		panic(err.Error())
	}	
	stmtUpd, err := db.Prepare("Update us set Name = ? where Id = ?")	
	if err != nil {
		panic(err.Error())
	}
	j := 0
	for i:=0 ; i<100 ; i++{
		time.Sleep(1000 * time.Millisecond)
		randNum := rand.Intn(10) % 3
		switch randNum{
			case 0:
				out,err := stmtIn.Exec(i,name[i%6], age[i%6],"unacademy")
				j++;
				if err != nil {
					panic(err.Error())
				}
				fmt.Println(out)
			case 1:
				if j>0 {
					out,err := stmtOut.Exec(rand.Intn(j))
					if err != nil {
						panic(err.Error())
					}
					fmt.Println(out)
				}
			case 2:
				if j > 0 {
					out,err := stmtUpd.Exec(name[i%6], rand.Intn(j))
					if err != nil {
						panic(err.Error())
					}
					fmt.Println(out)
				}
		}
		// fmt.Println(randNum)		time.Sleep(5000 * time.Millisecond)
	}
}