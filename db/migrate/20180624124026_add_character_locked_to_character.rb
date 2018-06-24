class AddCharacterLockedToCharacter < ActiveRecord::Migration[5.2]
  def change
    add_column :characters, :locked, :boolean, null: false, default: false
  end
end
