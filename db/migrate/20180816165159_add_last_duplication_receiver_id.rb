class AddLastDuplicationReceiverId < ActiveRecord::Migration[5.2]
  def change
    add_column :users, :last_duplication_receiver_id, :integer
  end
end
