SELECT region_id, regions.name region_name, eve_item_id, sum(volume) volume, sum(order_count) orders_count,
                  max(highest) max_price, min(lowest) min_price, avg(average) avg_price
FROM eve_market_histories, regions
WHERE eve_market_histories.region_id = regions.id
GROUP BY region_id, regions.name, eve_item_id;