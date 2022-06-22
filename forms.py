rodzaje = AllData(
    car=request.form.get("pojazd"),
    house=request.form.get("dom"),
    travel=request.form.get("podroz"),
    life=request.form.get("zycie"),
    agriculture=request.form.get("rolne"),
    company=request.form.get("firma")
)

# add_kind = Kind(car=request.form.get("pojazd"),
#                 house=request.form.get("dom"),
#                 travel=request.form.get("podroz"),
#                 life=request.form.get("zycie"),
#                 agriculture=request.form.get("rolne"),
#                 company=request.form.get("firma"))
# db.session.add(add_kind)
# db.session.commit()