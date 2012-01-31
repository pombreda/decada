# -*- coding: utf-8 -*-

hgUsefull = False
import shutil
import os
try:
	#noinspection PyUnresolvedReferences
	from mercurial import graphmod, __version__
	#noinspection PyUnresolvedReferences
	import hglib
	hgUsefull = True
except ImportError:
	hgUsefull = False

#####################################################################
## Global functions
#####################################################################
def version():
	return __version__.version

#####################################################################
## HgInter class - wrap HG operations
#####################################################################
class HgInter:
	"""Class implements operations with HG (Mercurial) repositories.
	Also, class implements switch between local repository for changes history,
	and remote, "master" repository. """
	def __init__(self, path = '', src = None, uname = '', passwd = ''):
		"""Initialize two repositories.
		Load local repository if exists. If not exists, clone from remote,
		or create new. 
		:param path:
		:param src:
		:param uname:
		:param passwd:
		"""
		global hgUsefull
		self.User = uname
		self.Password = passwd
		self.AddRemove = True
		self._client = None
		self._local = True
		self._repoPath = os.path.join(path, '.hg')
		self._repoPathLocal = os.path.join(path, '.hg-local')
		self._repoPathRemote = os.path.join(path, '.hg-remote')
		if hgUsefull:
			conf = ['auth.def.prefix=*',
			        '--config', 'auth.def.schemes=http https',
			        '--config', 'auth.def.username=%s' % self.User,
			        '--config', 'auth.def.password=%s' % self.Password]
			try:
				try:
					self._client = hglib.open(path, configs=conf)
				except hglib.error.ServerError:
					if src:
						self._client = hglib.clone(src, path, configs=conf)
						shutil.copytree(self._repoPath, self._repoPathRemote)
						self._client.open()
					else:
						self._client = hglib.init(path, configs=conf)
						shutil.copytree(self._repoPath, self._repoPathRemote)
						shutil.copytree(self._repoPath, self._repoPathLocal)
						self._client.open()
			except Exception:
				# not found HG?
				hgUsefull = False
		# initialised

	def IsOk(self):
		return hgUsefull and self._client is not None

	def reopen(self):
		if self._client:
			conf = ['auth.def.prefix=*',
			        '--config', 'auth.def.schemes=http https',
			        '--config', 'auth.def.username=%s' % self.User,
			        '--config', 'auth.def.password=%s' % self.Password]
			root = self._client.root()

			self._client.close()
			self._client = hglib.open(root, configs=conf)

	def status(self, rev=None):
		if self._client:
			return self._client.status(rev)
		return None

	def commit(self, message, files = None, closebranch=False):
		if self.IsOk():
			autos = self.AddRemove
			if files is not None:
				autos = False
			self._client.commit(message, include=files, addremove=autos, closebranch=closebranch, user=self.User)
		pass

	def push(self, remote, force=False, insecure=False):
		if not self.IsOk():
			return
		try:
			self.commit('Automatic commit before push')
		except Exception:
			pass
		self._client.push(remote, force=force, insecure=insecure)
		pass

	def sync(self, remote=None, rev=None, insecure=False, do_pull=True):
		if not self.IsOk():
			return
		if not remote and do_pull:
			# find the default remote repo
			pass
		if do_pull:
			self._client.pull(remote, insecure=insecure)
		self._client.update(rev=rev)
		pass

	def log(self, revrange=None, include_wd=False):
		result = []
		if self.IsOk():
			result = self._client.log(revrange=revrange)
			if include_wd:
				pass
		return result
	
	def colored(self, revrange=None, include_wd=False):
		log = self.log(revrange)
		num_revs = len(log)
		clog = []
		for rev in log:
			pl = self._client.parents(rev[0])
			if not pl:
				pl = []
			pl = [x[0] for x in pl]
			cr = (rev[0], 'C', rev[1], pl)
			clog.append(cr)
		if include_wd:
			# fakeID, hash, tags, branch, user, title, date
			rev = (len(log) + 1000, 'ffffffffffff', '', '', self.User, '** Working Directory **', '')
			log.insert(0, rev)
			pl = self._client.parents()
			if not pl:
				pl = []
			cr = (rev[0], 'C', rev[1], pl)
			clog.insert(0, cr)
		cres = graphmod.colored(clog)
		colors = {}
		for rev in cres:
			colors[rev[0]] = (rev[3], rev[4])
		for ii in xrange(len(log)):
			rev = log[ii]
			cr = (rev[0], rev[1], rev[2], rev[3], rev[4], rev[5], rev[6], colors[rev[0]][0], colors[rev[0]][1])
			log[ii] = cr
		if include_wd:
			rev = 0
			pl = self._client.parents()
			if pl:
				for p in pl:
					rev = max(rev, int(p[0]))
			else:
				rev = num_revs
			cr = log[0]
			log[0] = (str(rev) + '+', cr[1], cr[2], cr[3], cr[4], cr[5], cr[6], cr[7], cr[8])
		return log

	def SwitchToLocal(self):
		"""Switch to local repository if exists."""
		if self.IsOk() and not self._local:
			shutil.rmtree(self._repoPathRemote, ignore_errors=True)
			shutil.copytree(self._repoPath, self._repoPathRemote)
			if os.path.exists(self._repoPathLocal):
				shutil.rmtree(self._repoPath, ignore_errors=True)
				shutil.copytree(self._repoPathLocal, self._repoPath)
				self._client.close()
				self._client.open()
				self._local = True
			# if local copy exists
		# if remote copy active
		pass

	def SwitchToRemote(self):
		if self.IsOk() and self._local:
			shutil.rmtree(self._repoPathLocal, ignore_errors=True)
			shutil.copytree(self._repoPath, self._repoPathLocal)
			if os.path.exists(self._repoPathRemote):
				shutil.rmtree(self._repoPath, ignore_errors=True)
				shutil.copytree(self._repoPathRemote, self._repoPath)
				self._client.close()
				self._client.open()
				self._local = False
			# if remote copy exists
		# if local copy active
		pass

	@property
	def Repo(self):
		return self._client

	@property
	def Local(self):
		return self._local

	@property
	def IsWdChanged(self):
		return len(self.status()) > 0
