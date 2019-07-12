FactoryBot.define do
  factory :buy_orders_analytic do

    approx_max_price { 200 }
    over_approx_max_price_volume { 150 }
    single_unit_cost { 150 }
    single_unit_margin { 50 }
    estimated_volume_margin { 150 }
    per_job_margin { 10 }
    per_job_run_margin { 25 }
    final_margin { 26 }

  end
end
