

def store_performance() -> List[Dict[str, Any]]:
    """
    get Revenue by store
    
    """
    query = """
    SELECT s.store_name,
           SUM(fs.total_amount) AS store_sales
    FROM fact_sales fs
    JOIN dim_store s ON fs.store_id = s.store_id
    GROUP BY s.store_name
    ORDER BY store_sales DESC;
    """
    return run_query(query).to_dict(orient="records")

