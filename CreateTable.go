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
	// name := [6]string{"Tat","Dad","cat", "dog", "mad", "goat"}
	// course :=[3]string{"Math","Phy", "Chem"}
	//age  := [6]int{5, 6, 4, 6, 3,10}
	// db,_:= sql.Open("mysql", "root:tatvam@/openhack")
	db,_:= sql.Open("mysql", "XXXXXXX:XXXXXXXX#@tcp(openhack-flydata.XXXXXXXXXXXXX.com:3306)/openhack")
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

}

