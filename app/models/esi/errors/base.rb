class Esi::Errors::Base < RuntimeError

  def self.dispatch( exception )
    case exception.message
    when '504 Gateway Timeout'
      raise Esi::Errors::GatewayTimeout
    when '502 Bad Gateway'
      raise Esi::Errors::BadGateway
    when '403 Forbidden'
      raise Esi::Errors::Forbidden
    else
      raise exception
    end
  end

end