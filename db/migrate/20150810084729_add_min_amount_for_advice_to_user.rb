class AddMinAmountForAdviceToUser < ActiveRecord::Migration
  def change
    add_column :users, :min_amount_for_advice, :float
  end
end
