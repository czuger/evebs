class AddMinPcentForAdvice < ActiveRecord::Migration[4.2]
  def change
    add_column :users, :min_pcent_for_advice, :integer
  end
end
