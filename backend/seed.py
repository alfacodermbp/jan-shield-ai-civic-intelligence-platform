from .app import conn, init_db, uid, now
def main():
    init_db()
    with conn() as c:
        user=uid('U-'); c.execute('INSERT OR IGNORE INTO users VALUES(?,?,?,?,?,?,?)',(user,'Synthetic Demo Citizen','citizen@demo.local','CITIZEN',None,now(),now()))
        for name,cat in [('Municipal Sanitation','Waste Management'),('Streetlight Department','Streetlights'),('Water Supply Board','Water Supply'),('Roads Division','Roads')]: c.execute('INSERT OR IGNORE INTO departments VALUES(?,?,?,?,?,?)',(uid('D-'),name,cat,'demo contact',1,now()))
        for i in range(30): c.execute('INSERT INTO complaints VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(uid('C-'),user,f'Garbage not collected - Ward 17 #{i+1}',f'Bhaiya {5+i%4} din se kachra nahi utha near school. Many residents report overflowing waste and health risk. Photo available.', 'Waste Management','Ward 17 school vicinity',21.19+(i%5)*.001,81.35+(i%5)*.001,'17','HIGH','HIGH','SUBMITTED',None,None,None,now(),now()))
        for cat in ('Streetlights','Water Supply','Roads'):
            for i in range(5): c.execute('INSERT INTO complaints VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(uid('C-'),user,f'{cat} service complaint #{i+1}',f'Synthetic demo {cat.lower()} issue reported for several days in Ward {10+i}.','Other',f'Ward {10+i}',21.2,81.36,str(10+i),'MEDIUM','MEDIUM','SUBMITTED',None,None,None,now(),now()))
    print('Seeded synthetic JAN-SHIELD demo data.')
if __name__=='__main__': main()
