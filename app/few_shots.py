few_shots_questions = [
    {
        "input": "How many pant do we have left for Nike in XS size and white color?",
        "SQLQuery": "SELECT sum(stock_quantity) FROM products WHERE brand = 'Nike' AND color = 'White' AND size = 'XS'",
        "SQLResult": "Result of the SQL query",
        "Answer": "91",
    },
    {
        "input": "How many tshirt do we have for Adidas brand and  white color?",
        "SQLQuery": "SELECT Count(*) FROM products WHERE brand = 'Adidas' AND color = 'White'",
        "SQLResult": "Result of the SQL query",
        "Answer": "91",
    },
    {
        "input": "How much is the total price of the inventory for all XL size t-shirts?",
        "SQLQuery": "SELECT SUM(price*stock_quantity) FROM t_shirts WHERE size = 'XL'",
        "SQLResult": "Result of the SQL query",
        "Answer": "22292",
    },
    {
        "input": "How many white color Levi's trouser I have?",
        "SQLQuery": "SELECT sum(stock_quantity) FROM trouser WHERE brand = 'Levi' AND color = 'White'",
        "SQLResult": "Result of the SQL query",
        "Answer": "290",
    },
    {
        "input": "how much sales amount will be generated if we sell all large size t shirts today in nike brand after discounts?",
        "SQLQuery": """SELECT sum(a.total_amount * ((100-COALESCE(discounts.pct_discount,0))/100)) as total_revenue from
(select sum(price*stock_quantity) as total_amount, t_shirt_id from t_shirts where brand = 'Nike' and size="L"
group by t_shirt_id) a left join discounts on a.t_shirt_id = discounts.t_shirt_id
 """,
        "SQLResult": "Result of the SQL query",
        "Answer": "290",
    },
]
