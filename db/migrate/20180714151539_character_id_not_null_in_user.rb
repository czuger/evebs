class CharacterIdNotNullInUser < ActiveRecord::Migration[5.2]
  def change
    change_column :users, :current_character_id, :bigint, null: false
  end
end
