module Esi::Errors
  class UnknownError < Base

    def pause
      sleep 60*3
    end

    def retry?
      true
    end

  end
end
