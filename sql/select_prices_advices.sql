SELECT *, (min_price*batch_size_formula)-(single_unit_cost*batch_size_formula) margin_comp_immediate,
          (price_avg_week*batch_size_formula)-(single_unit_cost*batch_size_formula) margin_comp_weekly
FROM ( SELECT re.name region_name,
             tu.name trade_hub_name,
             ei.name item_name,
             single_unit_cost,
             min_price,
             avg_price,
             price_avg_week,
             vol_month,
             vol_day,
             history_volume,
             full_batch_size,
             prod_qtt,
             daily_monthly_pcent,
             margin_percent,
             CASE
               WHEN $1
                       THEN LEAST(full_batch_size, FLOOR(history_volume * $2 ))
               ELSE FLOOR(history_volume * $2 )
                 END batch_size_formula
      FROM prices_advices pa
             JOIN eve_items ei ON pa.eve_item_id = ei.id
             JOIN trade_hubs tu ON pa.trade_hub_id = tu.id
             JOIN regions re ON re.id = tu.region_id
             WHERE history_volume IS NOT NULL ) prices_advices_sub_1