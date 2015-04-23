class AddMinPcentForAdvice < ActiveRecord::Migration
  def change
    add_column :users, :min_pcent_for_advice, :integer
  end
end
