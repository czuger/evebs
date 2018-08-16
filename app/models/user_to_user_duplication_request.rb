class UserToUserDuplicationRequest < ApplicationRecord

  SALES_ORDERS = 1
  PRODUCTION_LIST = 2

  belongs_to :sender, class_name: 'User'

end
